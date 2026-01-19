# Mural PDF to CSV Converter

This script extracts table data (like threat models) from a Mural PDF export and converts it to a CSV file that can be uploaded to Google Sheets.

## Installation

Ensure you have Python installed, then install the required library:

```bash
pip install pdfplumber
```

## Usage

1.  Export your Mural as a **PDF**.
2.  Place the PDF in this folder (or provide the full path).
3.  Run the script:

```bash
python mural_pdf_to_csv.py "your_mural_export.pdf"
```

The script will generate `mural_data.csv` by default.

## Importing to Google Sheets

1.  Open a Google Spreadsheet.
2.  Go to **File > Import**.
3.  Select **Upload** and choose the generated `mural_data.csv`.
4.  Choose "Append to current sheet" or "Replace spreadsheet".
