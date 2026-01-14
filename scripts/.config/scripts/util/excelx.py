"Utilities for managing excel files"

import click
from pathlib import Path
from decouple import config
from datetime import date

import xlwings as xw
import pandas as pd

# Legacy password
LEGACY = config("LEGACY", cast=str)


def create_excel_from_template(
    template_path: Path,
    template_name: str,
    new_path: Path,
    new_file_name: str,
    jobcode="",
    version="B0",
) -> None:
    try:
        if (new_path / new_file_name).exists():
            click.echo(f"'{new_file_name}' already exists. Aborted.")
            return
        # Run excel in the backgroud
        click.echo("Creating excel file. May take a while...")
        with xw.App(visible=False) as app:
            # create workbook from template
            wb = app.books.open(Path(template_path, template_name), password=LEGACY)
            # write default values
            wb.sheets("config").range("B29").value = jobcode
            wb.sheets("config").range("B30").value = version
            wb.sheets("config").range("B32").value = date.today().strftime("%Y-%m-%d")
            # save the workbook as new file
            wb.save(Path(new_path, new_file_name), password=LEGACY)
            # close the workbook
            wb.close()
            click.echo(f"Created {new_file_name}")
    except Exception:
        click.echo("Error creating excel file.")


def set_format(
    wb: xw.Book, font_name: str = "Arial", font_size: int = 12
) -> None:
    "Set font attributes in workbook"
    for sheet in wb.sheets:
        try:
            sheet.used_range.font.name = font_name
            sheet.used_range.font.size = font_size
        except Exception:
            click.echo(f"Beautifying excel sheet '{sheet.name}' not successful.")


def set_column_width_by_content(
    wb: xw.Book, max_width: int = 80, min_width: int = 8
) -> None:
    """
    Set column width based on average content length.

    - Calculates average content length per column (avoids outlier skew)
    - Caps width at max_width characters
    - Enables word wrap for cells exceeding the column width
    - Sets minimum width to min_width
    """
    for sheet in wb.sheets:
        try:
            used_range = sheet.used_range
            if used_range is None:
                continue

            # Get all values as a 2D list
            values = used_range.value
            if values is None:
                continue

            # Handle single cell case
            if not isinstance(values, list):
                values = [[values]]
            # Handle single row case
            elif not isinstance(values[0], list):
                values = [values]

            num_cols = len(values[0]) if values else 0

            for col_idx in range(num_cols):
                lengths = []

                for row in values:
                    if col_idx < len(row) and row[col_idx] is not None:
                        cell_value = str(row[col_idx])
                        # For multiline content, get the longest line
                        lines = cell_value.split("\n")
                        line_max = max(len(line) for line in lines)
                        lengths.append(line_max)

                # Calculate average length, default to min_width if no data
                if lengths:
                    avg_len = sum(lengths) / len(lengths)
                else:
                    avg_len = min_width

                # Use average but ensure minimum width
                col_width = max(avg_len, min_width)
                # Cap at max_width
                col_width = min(col_width, max_width)

                # Get the column range (1-indexed in xlwings)
                col_range = used_range.columns[col_idx]

                # Set column width (add small padding for readability)
                col_range.column_width = col_width + 2

                # Enable word wrap for cells exceeding the column width
                if lengths and max(lengths) > col_width:
                    col_range.wrap_text = True

            # Auto-fit row heights to show wrapped text
            used_range.rows.autofit()

            click.echo(f"Set column widths for sheet '{sheet.name}'")
        except Exception as e:
            click.echo(f"Error setting column width for sheet '{sheet.name}': {e}")


if __name__ == "__main__":
    pass
