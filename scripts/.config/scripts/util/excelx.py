"Utilities for managing excel files"

import click
from pathlib import Path
from decouple import config
from datetime import date

import xlwings as xw

# import pandas as pd

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
    wb: xw.Book, font_name: str = "Aptos Narrow", font_size: int = 11
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


def is_numeric_like(value) -> bool:
    """
    Check if a value is numeric-like (numbers, currency, dates).
    These cannot wrap in Excel and will show as ### if too wide.
    """
    import re
    from datetime import datetime

    # Already a number or date type
    if isinstance(value, (int, float, datetime)):
        return True

    # String that looks like a number or currency
    if isinstance(value, str):
        s = value.strip()
        # Currency patterns: $1,234.56 or 1,234.56 USD or €1.234,56
        currency_pattern = r"^[\$€£¥₹]?\s*[\d,.\s]+[\$€£¥₹]?\s*[A-Z]{0,3}$"
        if re.match(currency_pattern, s):
            return True
        # Plain number with possible thousands separators
        try:
            # Remove common thousand separators and try to parse
            cleaned = s.replace(",", "").replace(" ", "")
            float(cleaned)
            return True
        except ValueError:
            pass

    return False


def set_column_width_by_content(
    wb: xw.Book, max_width: int = 80, min_width: int = 8
) -> None:
    """
    Set column width based on average content length of table data.

    - Detects table start (skips headers/project info at top)
    - Calculates average content length per column from table data (avoids outlier skew)
    - Scans ALL data (including headers, merged cells) for numeric values
    - Ensures numeric values (which can't wrap) always fit to avoid ###
    - Caps width at max_width characters
    - Enables word wrap for text cells exceeding the column width
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

            # Use all data for column count (not just table data)
            num_cols = max(len(row) if isinstance(row, list) else 1 for row in values)

            for col_idx in range(num_cols):
                lengths = []  # For average calculation (table data only)
                max_numeric_len = 0  # Track longest numeric in ALL data

                # Scan ALL data for numeric values (they can't wrap, show as ###)
                for row in values:
                    if not isinstance(row, list):
                        row = [row]
                    if col_idx < len(row) and row[col_idx] is not None:
                        cell_value = row[col_idx]
                        cell_str = str(cell_value)
                        if not cell_str.strip():
                            continue
                        # For multiline content, get the longest line
                        lines = cell_str.split("\n")
                        line_max = max(len(line) for line in lines)

                        # Track max numeric length from ALL rows
                        if is_numeric_like(cell_value):
                            max_numeric_len = max(max_numeric_len, line_max)

                # Calculate average from table data only (avoids header skew)
                for row in table_data:
                    if not isinstance(row, list):
                        row = [row]
                    if col_idx < len(row) and row[col_idx] is not None:
                        cell_value = row[col_idx]
                        cell_str = str(cell_value)
                        if not cell_str.strip():
                            continue
                        lines = cell_str.split("\n")
                        line_max = max(len(line) for line in lines)
                        lengths.append(line_max)

                # Get the column range
                try:
                    col_range = used_range.columns[col_idx]
                except Exception:
                    # Skip if merged cells cause issues
                    continue

                # If no data in column at all, set width to 0
                if not lengths and max_numeric_len == 0:
                    try:
                        col_range.column_width = 0
                    except Exception:
                        pass
                    continue

                # Calculate average length from table data (if available)
                if lengths:
                    avg_len = sum(lengths) / len(lengths)
                    col_width = max(avg_len, min_width)
                else:
                    # No table data, start with minimum
                    col_width = min_width

                # Ensure numeric values fit (they can't wrap, will show as ###)
                # This covers numeric data anywhere in the sheet
                if max_numeric_len > col_width:
                    col_width = max_numeric_len

                # Cap at max_width
                col_width = min(col_width, max_width)

                # Set column width (add small padding for readability)
                try:
                    col_range.column_width = col_width + 2
                except Exception:
                    # Skip if merged cells cause issues
                    pass

                # Enable word wrap for text cells exceeding the column width
                # (numeric cells won't wrap anyway)
                if lengths and max(lengths) > col_width:
                    # Only wrap text in table data rows
                    try:
                        table_range = sheet.range(
                            used_range.row + table_start,
                            used_range.column + col_idx,
                            used_range.row + len(values) - 1,
                            used_range.column + col_idx,
                        )
                        table_range.wrap_text = True
                    except Exception:
                        # Skip if merged cells cause issues
                        pass

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
