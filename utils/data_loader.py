import re

import pandas as pd
import streamlit as st


def _fix_mojibake(text: str) -> str:
    if "Ã" in text or "Â" in text or "â" in text:
        try:
            return text.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    replacements = {
        "Ã¸": "ø",
        "Ã˜": "Ø",
        "Ã¦": "æ",
        "Ã†": "Æ",
        "Ã¥": "å",
        "Ã…": "Å",
        "Ã¼": "ü",
        "Ã¶": "ö",
        "Ã¤": "ä",
        "Ã©": "é",
        "Ã¨": "è",
        "Ã¢": "â",
        "Ã®": "î",
        "Ã´": "ô",
        "â€“": "–",
        "â€”": "—",
        "â€œ": "“",
        "â€": "”",
        "â€˜": "‘",
        "Â": "",
    }

    for wrong, right in replacements.items():
        if wrong in text:
            text = text.replace(wrong, right)

    return text


def clean_text(value):
    if value is None:
        return None

    text = str(value)
    if not text:
        return None

    text = text.strip()
    if not text:
        return None

    text = text.replace("\xa0", " ")
    text = _fix_mojibake(text)
    text = re.sub(r"\s+", " ", text)

    normalized = text.strip()
    if normalized.lower() in {"nan", "none", "na", "nat"}:
        return None

    return normalized


def clean_numeric(value):
    text = clean_text(value)
    if text is None:
        return None

    text = text.replace(",", ".")
    text = re.sub(r"[ \u00A0']", "", text)

    try:
        return float(text)
    except ValueError:
        return None


@st.cache_data
def load_and_clean_csv(path, sep=";", encoding="utf-8", dtype=str, na_values=None, usecols=None):
    try:
        df = pd.read_csv(
            path,
            sep=sep,
            encoding=encoding,
            dtype=dtype,
            keep_default_na=False,
            na_values=na_values or ["nan", "NaN", "None", "none"],
            usecols=usecols,
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            path,
            sep=sep,
            encoding="latin1",
            dtype=dtype,
            keep_default_na=False,
            na_values=na_values or ["nan", "NaN", "None", "none"],
            usecols=usecols,
        )

    df.columns = [clean_text(column) for column in df.columns]
    df = df.loc[:, [column for column in df.columns if column is not None]]

    df = df.apply(lambda column: column.map(clean_text))
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    return df
