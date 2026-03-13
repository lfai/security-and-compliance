import pdfplumber
import csv
import argparse
import os

def extract_tables_from_pdf(pdf_path, output_csv):
    """
    Extracts tables from a Mural PDF export and saves them to a CSV file.
    """
    all_data = []
    
    print(f"Opening PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"Processing page {i+1}...")
            tables = page.extract_tables()
            
            for table in tables:
                # Clean up the table: remove None values and replace newlines with spaces
                for row in table:
                    clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                    # Filter out rows that are entirely empty
                    if any(clean_row):
                        all_data.append(clean_row)
    
    if not all_data:
        print("No table data found in the PDF.")
        return False

    # Check if we have consistent headers. If not, we might need more logic.
    # For now, we'll just write all rows.
    
    print(f"Writing {len(all_data)} rows to {output_csv}")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(all_data)
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Extract table data from a Mural PDF export to CSV.")
    parser.add_argument("pdf", help="Path to the Mural PDF file.")
    parser.add_argument("--output", "-o", default="mural_data.csv", help="Output CSV filename.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf):
        print(f"Error: File '{args.pdf}' not found.")
        return

    if extract_tables_from_pdf(args.pdf, args.output):
        print(f"Successfully exported data to {args.output}")
    else:
        print("Failed to extract data.")

if __name__ == "__main__":
    main()
