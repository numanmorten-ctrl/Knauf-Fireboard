"""Helpers for building project-level material exports and ZIP packages."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from io import BytesIO
import json
from pathlib import PurePosixPath
from typing import Callable, Iterable
from urllib.parse import unquote, urlparse
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import requests

from utils.documentation_urls import (
    FIREBOARD_INSTALLATION_SECTION_URL,
    FIREBOARD_MANUAL_SECTION_URL,
)
from utils.export_helpers import (
    EXPORT_TYPE_COMBINED,
    EXPORT_TYPE_PER_CALCULATION,
    add_system_separator_rows,
    create_materials_excel,
    get_materials_excel_filename,
)

PROJECT_PACKAGE_MIME = "application/zip"


def _signature_normalize(value: object) -> object:
    """Return JSON-serializable project data for download cache keys."""

    if isinstance(value, pd.DataFrame):
        normalized_df = value.where(pd.notna(value), None)
        return {
            "columns": list(normalized_df.columns),
            "rows": normalized_df.to_dict(orient="records"),
        }

    if isinstance(value, dict):
        return {
            str(key): _signature_normalize(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }

    if isinstance(value, (list, tuple)):
        return [_signature_normalize(item) for item in value]

    if pd.isna(value):
        return None

    return value


def build_project_download_signature(
    *,
    calculations: list[dict],
    combined_materials: dict[str, pd.DataFrame],
    language: str,
    project_details: dict[str, object] | None = None,
) -> str:
    """Return a stable signature for cached project-level downloads."""

    payload = {
        "calculations": _signature_normalize(calculations),
        "combined_materials": _signature_normalize(combined_materials),
        "language": language,
        "project_details": _signature_normalize(project_details or {}),
    }
    serialized = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def get_cached_project_download(cache: dict | None, signature: str) -> object | None:
    """Return cached download data only when it matches the current signature."""

    if not cache or cache.get("signature") != signature:
        return None

    return cache.get("data")



@dataclass(frozen=True)
class ExternalProjectFile:
    """External file reference to include in the project package."""

    url: str
    folder: str
    filename: str
    label: str
    key: str


@dataclass(frozen=True)
class ProjectMaterialExports:
    """Generated material-list exports for a saved project."""

    combined_excel: BytesIO
    per_calculation_excel: BytesIO


def _bytes_from_filelike(filelike: BytesIO | bytes) -> bytes:
    """Return bytes without leaving a BytesIO object's cursor at EOF."""

    if isinstance(filelike, bytes):
        return filelike

    position = filelike.tell()
    filelike.seek(0)
    data = filelike.read()
    filelike.seek(position)
    return data


def _is_present(value: object) -> bool:
    """Return True when a CSV/dataframe value contains useful text."""

    text = str(value or "").strip()
    return bool(text) and text.lower() != "nan"


def _first_existing_column(
    dataframe: pd.DataFrame,
    candidates: Iterable[str],
) -> str | None:
    """Return the first candidate column that exists in the dataframe."""

    for column in candidates:
        if column in dataframe.columns:
            return column
    return None


def build_project_material_exports(
    combined_materials: dict[str, pd.DataFrame],
    language: str,
    t: Callable[[str], str],
) -> ProjectMaterialExports | None:
    """Create the combined and per-calculation Excel exports for a project."""

    if not combined_materials:
        return None

    combined_df = pd.concat(
        combined_materials.values(),
        ignore_index=True,
    )

    material_columns = {
        "artnr": t("material_artnr"),
        "dbnr": t("material_dbnr"),
        "manufacturer": t("material_manufacturer"),
        "description": t("material_description"),
        "consumption": t("material_consumption"),
        "unit": t("material_unit"),
        "total": t("material_total"),
    }

    column_fallbacks = {
        "artnr": ["ART.NR.", "ART.NO."],
        "dbnr": ["DB NR", "DB NO"],
        "manufacturer": ["PRODUCENT", "MANUFACTURER"],
        "description": ["BESKRIVELSE", "DESCRIPTION"],
        "consumption": ["FORBRUG PR. LBM", "CONSUMPTION PER LM"],
        "unit": ["ENHED", "UNIT"],
        "total": ["SAMLET MÆNGDE", "TOTAL QUANTITY"],
    }

    def normalize_material_column(key: str) -> str | None:
        target_column = material_columns[key]
        source_columns = []

        for column in [target_column, *column_fallbacks[key]]:
            if column in combined_df.columns and column not in source_columns:
                source_columns.append(column)

        if not source_columns:
            return None

        normalized_values = combined_df[source_columns[0]]

        for column in source_columns[1:]:
            normalized_values = normalized_values.combine_first(
                combined_df[column]
            )

        combined_df[target_column] = normalized_values
        combined_df.drop(
            columns=[column for column in source_columns if column != target_column],
            inplace=True,
        )
        return target_column

    artnr_col = normalize_material_column("artnr")
    dbnr_col = normalize_material_column("dbnr")
    manufacturer_col = normalize_material_column("manufacturer")
    description_col = normalize_material_column("description")
    consumption_col = normalize_material_column("consumption")
    unit_col = normalize_material_column("unit")
    total_col = normalize_material_column("total")

    combined_df["SORT_ORDER"] = 999

    material_sort_terms = [
        (1, ["Fireboard"]),
        (2, ["spartelmasse", "joint filler"]),
        (3, ["Fugestrimler", "Fiberglass joint tape"]),
        (4, ["Skrue", "Screw"]),
        (5, ["Vinkelprofil", "Angle profile"]),
        (6, ["Bjælkeprofil", "Beam profile"]),
        (7, ["PHL profil", "PHL Profile"]),
        (99, ["Stålklamme", "Steel clamp"]),
    ]

    if description_col:
        for order, terms in material_sort_terms:
            description_matches = False
            for text in terms:
                description_matches = (
                    description_matches
                    | combined_df[description_col]
                    .astype(str)
                    .str.contains(text, case=False, na=False)
                )
            combined_df.loc[description_matches, "SORT_ORDER"] = order

    for col in [consumption_col, total_col]:
        if col and col in combined_df.columns:
            combined_df[col] = pd.to_numeric(
                combined_df[col].astype(str).str.replace(",", ".", regex=False),
                errors="coerce",
            ).fillna(0)

    combined_export_df = add_system_separator_rows(
        combined_df.drop(columns=["SORT_ORDER"], errors="ignore")
    )

    if artnr_col:
        combined_df["GROUP_KEY"] = (
            combined_df[artnr_col].fillna("").astype(str).str.strip()
        )
    else:
        combined_df["GROUP_KEY"] = ""

    combined_df["GROUP_KEY"] = combined_df["GROUP_KEY"].replace("", pd.NA)

    if description_col:
        combined_df["GROUP_KEY"] = combined_df["GROUP_KEY"].fillna(
            combined_df[description_col]
        )

    combined_df["GROUP_KEY"] = combined_df["GROUP_KEY"].fillna(
        "FREMMED_MATERIALE"
    )

    combined_df = combined_df.sort_values(by="SORT_ORDER", kind="stable")

    aggregation_columns = {"SORT_ORDER": "first"}

    for col in [artnr_col, dbnr_col, manufacturer_col, description_col, unit_col]:
        if col:
            aggregation_columns[col] = "first"

    for col in [consumption_col, total_col]:
        if col:
            aggregation_columns[col] = "sum"

    total_materials_df = (
        combined_df.groupby(
            ["GROUP_KEY"],
            dropna=False,
            as_index=False,
            sort=False,
        )
        .agg(aggregation_columns)
        .drop(columns=["GROUP_KEY"])
    )

    sort_columns = ["SORT_ORDER"]
    if description_col:
        sort_columns.append(description_col)

    total_materials_df = total_materials_df.sort_values(
        by=sort_columns,
        kind="stable",
    )

    per_calculation_excel = create_materials_excel(
        combined_export_df,
        include_header=False,
        language=language,
        per_system=True,
        export_type=EXPORT_TYPE_PER_CALCULATION,
    )

    total_export_df = total_materials_df.drop(columns=["SORT_ORDER"], errors="ignore")

    combined_excel = create_materials_excel(
        total_export_df,
        language=language,
        export_type=EXPORT_TYPE_COMBINED,
    )

    return ProjectMaterialExports(
        combined_excel=combined_excel,
        per_calculation_excel=per_calculation_excel,
    )


def project_package_filename(language: str = "DA") -> str:
    """Return the localized project package ZIP filename."""

    if language == "EN":
        return "Project_package.zip"
    return "Projektpakke.zip"


def _folders(language: str) -> dict[str, str]:
    """Return localized folder names for files in the package."""

    if language == "EN":
        return {
            "report": "Report",
            "materials": "Material_lists",
            "fireboard": "Fireboard",
            "epd": "EPD",
            "datasheets": "Datasheets",
        }

    return {
        "report": "Rapport",
        "materials": "Materialelister",
        "fireboard": "Fireboard",
        "epd": "EPD",
        "datasheets": "Datablade",
    }


def _report_filename(language: str) -> str:
    if language == "EN":
        return "Knauf_Fireboard_Report.pdf"
    return "Knauf_Fireboard_Rapport.pdf"


def _safe_filename(value: str, default: str, extension: str = ".pdf") -> str:
    """Create a zip-safe filename from user/URL/CSV values."""

    cleaned = "".join(
        character if character.isalnum() or character in "._-" else "_"
        for character in str(value or "").strip()
    ).strip("._-")
    if not cleaned:
        cleaned = default

    suffix = PurePosixPath(cleaned).suffix
    if not suffix:
        cleaned = f"{cleaned}{extension}"

    return cleaned


def _filename_from_url(url: str, default: str) -> str:
    """Best-effort filename from a URL path, falling back to a stable default."""

    path_name = unquote(PurePosixPath(urlparse(url).path).name)
    if path_name and "." in path_name:
        return _safe_filename(path_name, default)
    return _safe_filename(default, default)


def _material_lookup_maps(
    materials_lookup_records: Iterable[dict],
) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict]]:
    by_artnr = {}
    by_dbnr = {}
    by_description = {}

    for row in materials_lookup_records:
        artnr = str(row.get("ART.NR.", "") or "").strip()
        dbnr = str(row.get("DB_NR.", "") or "").strip()
        description_da = str(row.get("BESKRIVELSE_DK", "") or "").strip().lower()
        description_en = str(row.get("BESKRIVELSE_EN", "") or "").strip().lower()

        if artnr:
            by_artnr[artnr] = row
        if dbnr:
            by_dbnr[dbnr] = row
        if description_da and description_da not in by_description:
            by_description[description_da] = row
        if description_en and description_en not in by_description:
            by_description[description_en] = row

    return by_artnr, by_dbnr, by_description


def _rows_for_project_materials(
    combined_materials: dict[str, pd.DataFrame],
) -> Iterable[dict]:
    """Yield material rows from saved project material lists."""

    for materials_df in combined_materials.values():
        artnr_col = _first_existing_column(materials_df, ["ART.NR.", "ART.NO."])
        dbnr_col = _first_existing_column(materials_df, ["DB NR", "DB NO"])
        description_col = _first_existing_column(
            materials_df,
            ["BESKRIVELSE", "DESCRIPTION"],
        )

        for _, row in materials_df.iterrows():
            yield {
                "artnr": row.get(artnr_col) if artnr_col else "",
                "dbnr": row.get(dbnr_col) if dbnr_col else "",
                "description": row.get(description_col) if description_col else "",
            }


def collect_project_external_files(
    combined_materials: dict[str, pd.DataFrame],
    materials_lookup_records: Iterable[dict],
    language: str = "DA",
) -> list[ExternalProjectFile]:
    """Collect unique EPD and datasheet URLs for products in saved calculations."""

    folders = _folders(language)
    by_artnr, by_dbnr, by_description = _material_lookup_maps(materials_lookup_records)
    unique: dict[str, ExternalProjectFile] = {}

    for row in _rows_for_project_materials(combined_materials):
        material = None
        artnr = str(row.get("artnr") or "").strip()
        dbnr = str(row.get("dbnr") or "").strip()
        description = str(row.get("description") or "").strip().lower()

        if artnr and artnr in by_artnr:
            material = by_artnr[artnr]
        elif dbnr and dbnr in by_dbnr:
            material = by_dbnr[dbnr]
        elif description and description in by_description:
            material = by_description[description]

        if not material:
            continue

        stable_id = (
            str(material.get("ART.NR.", "") or "").strip()
            or str(material.get("DB_NR.", "") or "").strip()
            or _safe_filename(description, "material", "")
        )
        label = (
            str(material.get("BESKRIVELSE_DK", "") or "").strip()
            or str(material.get("BESKRIVELSE_EN", "") or "").strip()
            or stable_id
        )

        for kind, url_column, folder_key, prefix in [
            ("epd", "EPD_URL", "epd", "EPD"),
            ("datasheet", "DATABLAD_URL", "datasheets", "Datablad"),
        ]:
            url = str(material.get(url_column, "") or "").strip()
            if not _is_present(url):
                continue

            dedupe_key = f"{kind}:{url or stable_id}"
            if dedupe_key in unique:
                continue

            default_filename = f"{prefix}_{stable_id}.pdf"
            unique[dedupe_key] = ExternalProjectFile(
                url=url,
                folder=folders[folder_key],
                filename=_filename_from_url(url, default_filename),
                label=label,
                key=dedupe_key,
            )

    return list(unique.values())


def _download_external_file(
    file_ref: ExternalProjectFile,
    fetcher: Callable | None = None,
    timeout: int = 20,
) -> bytes:
    """Download an external file, raising on network/HTTP errors."""

    fetch = fetcher or requests.get
    response = fetch(file_ref.url, timeout=timeout)

    if hasattr(response, "raise_for_status"):
        response.raise_for_status()

    return bytes(response.content)


def _write_external_files(
    archive: ZipFile,
    file_refs: Iterable[ExternalProjectFile],
    fetcher: Callable | None,
) -> list[str]:
    """Write external files to a zip archive and return skipped-file messages."""

    skipped = []
    used_paths = set()

    for file_ref in file_refs:
        archive_path = f"{file_ref.folder}/{file_ref.filename}"
        stem = PurePosixPath(file_ref.filename).stem
        suffix = PurePosixPath(file_ref.filename).suffix or ".pdf"
        counter = 2

        while archive_path in used_paths:
            archive_path = f"{file_ref.folder}/{stem}_{counter}{suffix}"
            counter += 1

        try:
            content = _download_external_file(file_ref, fetcher=fetcher)
        except Exception as exc:  # noqa: BLE001 - package should survive bad URLs
            skipped.append(f"- {file_ref.label}: {file_ref.url} ({exc})")
            continue

        if not content:
            skipped.append(f"- {file_ref.label}: {file_ref.url} (empty response)")
            continue

        archive.writestr(archive_path, content)
        used_paths.add(archive_path)

    return skipped


def create_project_package_zip(
    *,
    report_pdf: BytesIO | bytes,
    material_exports: ProjectMaterialExports | None,
    combined_materials: dict[str, pd.DataFrame],
    materials_lookup_records: Iterable[dict],
    language: str = "DA",
    fetcher: Callable | None = None,
) -> BytesIO:
    """Build a ZIP with report, material lists, Fireboard docs and product docs."""

    folders = _folders(language)
    output = BytesIO()

    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(
            f"{folders['report']}/{_report_filename(language)}",
            _bytes_from_filelike(report_pdf),
        )

        if material_exports is not None:
            archive.writestr(
                f"{folders['materials']}/{get_materials_excel_filename(language, EXPORT_TYPE_COMBINED)}",
                _bytes_from_filelike(material_exports.combined_excel),
            )
            archive.writestr(
                f"{folders['materials']}/{get_materials_excel_filename(language, EXPORT_TYPE_PER_CALCULATION)}",
                _bytes_from_filelike(material_exports.per_calculation_excel),
            )

        fireboard_files = [
            ExternalProjectFile(
                url=FIREBOARD_MANUAL_SECTION_URL,
                folder=folders["fireboard"],
                filename="Fireboard_manualafsnit.pdf",
                label="Fireboard manualafsnit",
                key="fireboard:manual",
            ),
            ExternalProjectFile(
                url=FIREBOARD_INSTALLATION_SECTION_URL,
                folder=folders["fireboard"],
                filename="Fireboard_montageafsnit.pdf",
                label="Fireboard montageafsnit",
                key="fireboard:montage",
            ),
        ]
        product_files = collect_project_external_files(
            combined_materials,
            materials_lookup_records,
            language=language,
        )
        skipped = _write_external_files(
            archive,
            [*fireboard_files, *product_files],
            fetcher,
        )

        if skipped:
            readme_title = (
                "Some external files could not be downloaded and were skipped."
                if language == "EN"
                else "Nogle eksterne filer kunne ikke hentes og blev udeladt."
            )
            archive.writestr(
                "README.txt",
                "\n".join([readme_title, "", *skipped]),
            )

    output.seek(0)
    return output
