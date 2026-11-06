# Knauf Fireboard prototype

Prototype for dimensioning steel fire protection with Knauf Fireboard, estimating
materials, and exporting calculation and project documentation.

## Setup and start

Use Python 3.11 or newer. Extract the repository ZIP, open a terminal in its root
folder (the folder containing `app.py`), and create a virtual environment:

```sh
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in Windows PowerShell, or
`source .venv/bin/activate` on macOS/Linux. Then install the application dependencies
and start Fireboard:

```sh
python -m pip install -r requirements.txt
python -X utf8 -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.
Run from the repository root: datasets, illustrations and PDF templates use the
existing directory structure. The application does not require API credentials.

## Automated tests

In the same virtual environment and repository root, install the development
dependencies, which include the application dependencies and `pytest`:

```sh
python -m pip install -r requirements-dev.txt
python -X utf8 -m pytest
```

The UTF-8 option ensures consistent reading of Danish source text on Windows.
To run only the PDF date, daylight-saving and description-layout regression tests:

```sh
python -X utf8 -m pytest test_pdf_report_fields.py
```

Tests use the supplied calculation data, illustrations and report templates.
Keep these files together when extracting or moving the prototype.

## Handover contents and external documents

- `data/`: calculation tables, component rules and product/environmental data.
- `images/` and `static/`: profile and encasement illustrations, geometry guides
  and interface icons.
- `PDF_template.pdf` and `PDF_template_EN.pdf`: Danish and English report templates.
- [Requirements v1.1](docs/requirements/v1.1/): approved Danish and English
  specifications in Markdown, Word and PDF.
- [As-built functional specification](docs/functional-specification.md) and the
  original [Danish](docs/fireboard-requirements-specification-da.md) and
  [English](docs/fireboard-requirements-specification.md) requirements documents:
  unchanged reference material; v1.1 remains the current requirements specification.

The design and installation documents linked in `utils/documentation_urls.py`
are downloaded from Knauf. Product EPD and datasheet links in `data/materials.csv`
point to Knauf and ÖKOBAUDAT. The interface header logo also uses a Knauf-hosted
image. These intentionally external resources require internet access and are
not bundled with the repository ZIP. Calculations use the local datasets; the
prototype does not require a live EPIM connection.

Project documentation ZIP exports attempt to download the applicable external
documents. Failed or empty downloads are omitted and listed in the generated
`README.txt`. PDF reports and Excel material lists use the local templates and
assets.
