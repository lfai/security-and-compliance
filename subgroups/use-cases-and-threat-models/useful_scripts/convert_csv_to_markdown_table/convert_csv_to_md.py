#!/usr/bin/env python3
import csv
import os
import sys

def csv_to_markdown(csv_file_path: str):
    """Convert a CSV file to a Markdown table and save it as .md"""

    if not os.path.isfile(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' does not exist.")
        sys.exit(1)

    md_file_path = os.path.splitext(csv_file_path)[0] + ".md"

    # Open CSV with proper handling of quoted fields
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        rows = list(reader)

    if not rows:
        print("CSV is empty!")
        sys.exit(1)

    md_lines = []

    # Header
    header = rows[0]
    md_lines.append("| " + " | ".join(header) + " |")
    md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    # Data rows
    for row in rows[1:]:
        escaped_row = []
        for cell in row:
            # Escape | to avoid breaking Markdown table
            cell = cell.replace("|", "\\|")
            # Replace newlines inside cells with <br>
            cell = cell.replace("\r\n", "<br>").replace("\n", "<br>")
            # Optional: strip leading/trailing whitespace
            cell = cell.strip()
            escaped_row.append(cell)
        md_lines.append("| " + " | ".join(escaped_row) + " |")

    # Save to Markdown file
    with open(md_file_path, "w", encoding='utf-8') as mdfile:
        mdfile.write("\n".join(md_lines))

    print(f"Markdown table saved to {md_file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <csv_file_path>")
        sys.exit(1)

    csv_file = sys.argv[1]
    csv_to_markdown(csv_file)
