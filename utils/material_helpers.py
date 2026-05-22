import pandas as pd

from utils.data_loader import clean_numeric


# ---------------------------------------------------
# HELPER: Resolve screw/clamp for a single layer
# ---------------------------------------------------

def resolve_screw_clamp_by_layer(
    layer_no_val,
    board_mm_val,
    screw_rate_qty,
    staple_rate_qty,
    screw_clamp_logic_df,
    materials_by_artnr,
    materials_by_dbnr
):
    """
    For a given layer and board thickness,
    resolve and return screws/clamps.
    """

    resolved_materials = []

    # Find matching screw/clamp definition

    screw_clamp_lookup = screw_clamp_logic_df[
        (
            screw_clamp_logic_df["layer_no"]
            .map(clean_numeric)
            .fillna(0)
            ==
            layer_no_val
        )
        &
        (
            screw_clamp_logic_df["board_mm"]
            .map(clean_numeric)
            .fillna(0)
            .astype(int)
            ==
            int(board_mm_val)
        )
    ]

    if screw_clamp_lookup.empty:
        return resolved_materials

    screw_code = screw_clamp_lookup.iloc[0]["screw"]
    clamp_code = screw_clamp_lookup.iloc[0]["clamp"]

    # Resolve screw

    if (
        screw_rate_qty > 0
        and not pd.isna(screw_code)
        and str(screw_code).strip()
    ):

        screw_material = lookup_material_by_code(
            str(screw_code).strip(),
            materials_by_artnr,
            materials_by_dbnr
        )

        if screw_material is not None:

            resolved_materials.append({
                "Materiale": screw_material["BESKRIVELSE_DK"],
                "Mængde": screw_rate_qty,
                "Enhed": "stk"
            })

    # Resolve clamp

    if (
        staple_rate_qty > 0
        and not pd.isna(clamp_code)
        and str(clamp_code).strip()
    ):

        clamp_material = lookup_material_by_code(
            str(clamp_code).strip(),
            materials_by_artnr,
            materials_by_dbnr
        )

        if clamp_material is not None:

            resolved_materials.append({
                "Materiale": clamp_material["BESKRIVELSE_DK"],
                "Mængde": staple_rate_qty,
                "Enhed": "stk"
            })

    return resolved_materials


# ---------------------------------------------------
# HELPER: Lookup material by ART.NR. or DB_NR.
# ---------------------------------------------------

def lookup_material_by_code(
    code,
    materials_by_artnr,
    materials_by_dbnr
):
    """
    Lookup a material by article number or DB number.
    """

    if not code or not isinstance(code, str):
        return None

    code = str(code).strip()

    if not code:
        return None

    # Try ART.NR first

    if code in materials_by_artnr:
        return materials_by_artnr[code]

    # Fallback DB_NR

    if code in materials_by_dbnr:
        return materials_by_dbnr[code]

    return None


# ---------------------------------------------------
# HELPER: Lookup material info
# ---------------------------------------------------

def lookup_material_info(
    label,
    materials_by_artnr,
    materials_by_dbnr,
    materials_by_description
):
    """
    Lookup full material info from label.
    """

    if not isinstance(label, str):
        return None

    label = label.strip()

    if not label:
        return None

    # Formatted label

    if " · " in label:

        parts = [part.strip() for part in label.split("·")]

        if len(parts) >= 3:

            art_nr = parts[0]
            db_nr = parts[1]
            description = parts[2]

            if art_nr and art_nr in materials_by_artnr:
                return materials_by_artnr[art_nr]

            if db_nr and db_nr in materials_by_dbnr:
                return materials_by_dbnr[db_nr]

            description_lower = description.lower().strip()

            if description_lower in materials_by_description:
                return materials_by_description[description_lower]

    # Exact description

    label_lower = label.lower()

    if label_lower in materials_by_description:
        return materials_by_description[label_lower]

    # Partial search

    for description_lower, row in materials_by_description.items():

        if label_lower in description_lower:
            return row

    return None


# ---------------------------------------------------
# HELPER: Deduplicate materials
# ---------------------------------------------------

def deduplicate_materials(
    materials_list,
    materials_by_artnr,
    materials_by_dbnr,
    materials_by_description
):
    """
    Merge identical materials and sum quantities.
    """

    if not materials_list:
        return []

    deduplicated = {}

    for material in materials_list:

        label = str(material.get("Materiale", "")).strip()

        quantity = (
            clean_numeric(material.get("Mængde", 0))
            or 0
        )

        unit = str(material.get("Enhed", "")).strip()

        mat_info = lookup_material_info(
            label,
            materials_by_artnr,
            materials_by_dbnr,
            materials_by_description
        )

        primary_code = ""

        if mat_info is not None:

            primary_code = str(
                mat_info.get("ART.NR.", "")
            ).strip()

            if not primary_code:

                primary_code = str(
                    mat_info.get("DB_NR.", "")
                ).strip()

        if primary_code:

            group_key = (primary_code, unit)

        else:

            normalized_label = (
                " ".join(label.split()).lower()
            )

            group_key = (normalized_label, unit)

        if group_key not in deduplicated:

            deduplicated[group_key] = {
                "Materiale": label,
                "Mængde": quantity,
                "Enhed": unit
            }

        else:

            existing_qty = (
                clean_numeric(
                    deduplicated[group_key]["Mængde"]
                )
                or 0
            )

            deduplicated[group_key]["Mængde"] = (
                existing_qty + quantity
            )

    return list(deduplicated.values())


# ---------------------------------------------------
# FORMAT HELPERS
# ---------------------------------------------------

def format_number(value):

    try:
        value = float(value)

    except Exception:
        return ""

    return f"{value:.2f}".replace(".", ",")


def format_db_nr(value):

    if value is None:
        return ""

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none"}:
        return ""

    text = text.replace(" ", "")
    text = text.replace(",", "")

    if "." in text:
        text = text.split(".", 1)[0]

    return text


def format_art_nr(value):

    if value is None:
        return ""

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none"}:
        return ""

    text = text.replace(" ", "")

    if "." in text:
        text = text.split(".", 1)[0]

    return text.zfill(8)


# ---------------------------------------------------
# BUILD MATERIAL ROW
# ---------------------------------------------------

def build_material_row(
    row,
    profile_length,
    materials_by_artnr,
    materials_by_dbnr,
    materials_by_description
):

    match = lookup_material_info(
        row.get("Materiale", ""),
        materials_by_artnr,
        materials_by_dbnr,
        materials_by_description
    )

    per_meter = row.get("Mængde", 0)

    total = per_meter * profile_length

    return {

        "ART.NR.": (
            format_art_nr(match["ART.NR."])
            if match is not None
            else ""
        ),

        "DB_NR": (
            format_db_nr(match["DB_NR."])
            if match is not None
            else ""
        ),

        "PRODUCENT": (
            match["PRODUCENT"]
            if match is not None
            else ""
        ),

        "BESKRIVELSE": (
            match["BESKRIVELSE_DK"]
            if match is not None
            else row.get("Materiale", "")
        ),

        "FORBRUG": format_number(per_meter),

        "ENHED": row.get("Enhed", ""),

        "SPILDPROCENT": "",

        "SAMLET FORBRUG": format_number(total)
    }

def build_materials_dataframe(
    materials,
    profile_length,
    materials_by_artnr,
    materials_by_dbnr,
    materials_by_description
):

    materials_deduplicated = deduplicate_materials(
        materials,
        materials_by_artnr,
        materials_by_dbnr,
        materials_by_description
    )

    materials_df = pd.DataFrame(
        [
            build_material_row(
                row,
                profile_length,
                materials_by_artnr,
                materials_by_dbnr,
                materials_by_description
            )
            for _, row in pd.DataFrame(materials_deduplicated).iterrows()
        ],
        columns=[
            "ART.NR.",
            "DB_NR",
            "PRODUCENT",
            "BESKRIVELSE",
            "FORBRUG",
            "ENHED",
            "SPILDPROCENT",
            "SAMLET FORBRUG"
        ]
    )

    return materials_df

def get_material_label(df, search_terms, fallback="Ukendt materiale"):

    if "BESKRIVELSE_DK" not in df.columns:
        return fallback

    df["search_text"] = (
        df["BESKRIVELSE_DK"]
        .astype(str)
        .map(clean_text)
    )

    search_terms = [
        clean_text(term)
        for term in search_terms
    ]

    for term in search_terms:

        matches = df[
            df["search_text"] == term
        ]

        if not matches.empty:

            row = matches.iloc[0]

            return (
                f"{row['ART.NR.']} · "
                f"{row['DB_NR.']} · "
                f"{row['BESKRIVELSE_DK']}"
            )

    return fallback

def resolve_beam_text(
    beam_profile_logic_df,
    beam_type,
    clean_text
):
    """
    Resolve beam profile text from beam profile logic table.

    Returns:
        "PDP"
        or
        "BJ xx-xx color"
    """

    beam_lookup = beam_profile_logic_df[
        beam_profile_logic_df["profile"]
        .astype(str)
        .str.upper()
        ==
        str(beam_type).upper()
    ]

    if not beam_lookup.empty:

        beam_row = beam_lookup.iloc[0]

        bj_value = clean_text(
            beam_row.get("bj", "")
        )

        color_value = clean_text(
            beam_row.get("color", "")
        )

        pdp_value = clean_text(
            beam_row.get("pdp", "")
        )

        if bj_value and bj_value.lower() != "nan":

            bj_formatted = bj_value.replace("BJ", "BJ ")

            return f"Bjælkeprofil {bj_formatted} {color_value} 2000 mm".strip()

        elif pdp_value and pdp_value.lower() != "nan":

            return "PDP profil 25 3000 mm"

    return "PDP"
