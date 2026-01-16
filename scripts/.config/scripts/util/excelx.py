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


def find_table_start(values: list, min_columns: int = 3) -> int:
    """
    Detect where the table data starts by finding the header row.

    Heuristics:
    - A table header row has multiple consecutive non-empty cells
    - The rows following it also have similar structure (data rows)

    Returns the row index (0-based) where the table starts.
    """
    if not values:
        return 0

    num_rows = len(values)

    for row_idx in range(num_rows):
        row = values[row_idx]
        if not isinstance(row, list):
            row = [row]

        # Count non-empty cells in this row
        non_empty = sum(1 for cell in row if cell is not None and str(cell).strip())

        # Check if this looks like a header row (multiple columns filled)
        if non_empty >= min_columns:
            # Verify next row also has similar structure (it's actual table data)
            if row_idx + 1 < num_rows:
                next_row = values[row_idx + 1]
                if not isinstance(next_row, list):
                    next_row = [next_row]
                next_non_empty = sum(
                    1 for cell in next_row if cell is not None and str(cell).strip()
                )
                # If next row also has multiple values, this is likely the table header
                if next_non_empty >= min_columns:
                    return row_idx
            else:
                # Last row with multiple columns, assume it's a single-row table
                return row_idx

    # No table found, return 0 to process all data
    return 0


def set_column_width_by_content(
    wb: xw.Book, max_width: int = 80, min_width: int = 8
) -> None:
    """
    Set column width based on average content length of table data.

    - Detects table start (skips headers/project info at top)
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

            # Find where the table starts
            table_start = find_table_start(values)
            table_data = values[table_start:]

            if not table_data:
                continue

            num_cols = max(len(row) if isinstance(row, list) else 1 for row in table_data)

            for col_idx in range(num_cols):
                lengths = []

                for row in table_data:
                    if not isinstance(row, list):
                        row = [row]
                    if col_idx < len(row) and row[col_idx] is not None:
                        cell_value = str(row[col_idx])
                        # Skip empty strings
                        if not cell_value.strip():
                            continue
                        # For multiline content, get the longest line
                        lines = cell_value.split("\n")
                        line_max = max(len(line) for line in lines)
                        lengths.append(line_max)

                # Get the column range
                col_range = used_range.columns[col_idx]

                # If no data in column, set width to 0
                if not lengths:
                    col_range.column_width = 0
                    continue

                # Calculate average length
                avg_len = sum(lengths) / len(lengths)

                # Use average but ensure minimum width
                col_width = max(avg_len, min_width)
                # Cap at max_width
                col_width = min(col_width, max_width)

                # Set column width (add small padding for readability)
                col_range.column_width = col_width + 2

                # Enable word wrap for table cells exceeding the column width
                if max(lengths) > col_width:
                    # Only wrap text in table data rows
                    table_range = sheet.range(
                        used_range.row + table_start,
                        used_range.column + col_idx,
                        used_range.row + len(values) - 1,
                        used_range.column + col_idx,
                    )
                    table_range.wrap_text = True

            # Auto-fit row heights to show wrapped text
            used_range.rows.autofit()

            if table_start > 0:
                click.echo(
                    f"Set column widths for sheet '{sheet.name}' "
                    f"(table detected at row {table_start + 1})"
                )
            else:
                click.echo(f"Set column widths for sheet '{sheet.name}'")
        except Exception as e:
            click.echo(f"Error setting column width for sheet '{sheet.name}': {e}")


if __name__ == "__main__":
    pass
