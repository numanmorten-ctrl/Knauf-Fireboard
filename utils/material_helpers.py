        # ---------------------------------------------------
        # HELPER: Resolve screw/clamp for a single layer
        # ---------------------------------------------------
        def resolve_screw_clamp_by_layer(layer_no_val, board_mm_val, screw_rate_qty, staple_rate_qty):
            """
            For a given layer and board thickness, resolve and return screws/clamps.
            
            Args:
                layer_no_val: The layer number to match
                board_mm_val: The board thickness in mm
                screw_rate_qty: Per-meter quantity of screws to use if found
                staple_rate_qty: Per-meter quantity of clamps to use if found
            
            Returns:
                List of dictionaries with resolved screw/clamp materials
            """
            resolved_materials = []

        # ---------------------------------------------------
        # HELPER: Lookup material by ART.NR. or DB_NR.
        # ---------------------------------------------------
        def lookup_material_by_code(code):
            """
            Lookup a material by article number (ART.NR.) or database number (DB_NR.).
            Tries ART.NR. first, then falls back to DB_NR.
            
            Args:
                code: The article code to search for
            
            Returns:
                Material row dict or None if not found
            """
            if not code or not isinstance(code, str):
                return None

            code = str(code).strip()
            if not code:
                return None

            # Try ART.NR. first
            if code in materials_by_artnr:
                return materials_by_artnr[code]

            # Fallback to DB_NR.
            if code in materials_by_dbnr:
                return materials_by_dbnr[code]

            return None

        def deduplicate_materials(materials_list):
            """
            Group materials by ART.NR. (if available) and unit, sum quantities.
            This ensures screws/clamps from multiple layers are merged.
            
            Args:
                materials_list: List of material dicts with Materiale, Mængde, Enhed
            
            Returns:
                List of deduplicated material dicts
            """
            if not materials_list:
                return []

            deduplicated = {}

            for material in materials_list:
                label = str(material.get("Materiale", "")).strip()
                quantity = clean_numeric(material.get("Mængde", 0)) or 0
                unit = str(material.get("Enhed", "")).strip()

                mat_info = lookup_material_info(label)
                primary_code = ""
                if mat_info is not None:
                    primary_code = str(mat_info.get("ART.NR.", "")).strip()
                    if not primary_code:
                        primary_code = str(mat_info.get("DB_NR.", "")).strip()

                if primary_code:
                    group_key = (primary_code, unit)
                else:
                    normalized_label = " ".join(label.split()).lower()
                    group_key = (normalized_label, unit)

                if group_key not in deduplicated:
                    deduplicated[group_key] = {
                        "Materiale": label,
                        "Mængde": quantity,
                        "Enhed": unit
                    }
                else:
                    existing_qty = clean_numeric(deduplicated[group_key]["Mængde"]) or 0
                    deduplicated[group_key]["Mængde"] = existing_qty + quantity

            return list(deduplicated.values())

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

        def build_material_row(row):
            match = lookup_material_info(row.get("Materiale", ""))
            per_meter = row.get("Mængde", 0)
            total = per_meter * profile_length
            return {
                "ART.NR.": format_art_nr(match["ART.NR."]) if match is not None else "",
                "DB_NR": format_db_nr(match["DB_NR."]) if match is not None else "",
                "PRODUCENT": match["PRODUCENT"] if match is not None else "",
                "BESKRIVELSE": (
                    match["BESKRIVELSE_DK"] if match is not None else row.get("Materiale", "")
                ),
                "FORBRUG": format_number(per_meter),
                "ENHED": row.get("Enhed", ""),
                "SPILDPROCENT": "",
                "SAMLET FORBRUG": format_number(total)
            }
