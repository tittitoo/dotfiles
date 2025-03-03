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
    wb: xw.Book, font_name: str = "Arial", font_size: int = 12, autofit: bool = False
) -> None:
    "Set font attributes in workbook"
    for sheet in wb.sheets:
        sheet.used_range.font.name = font_name
        sheet.used_range.font.size = font_size
        if autofit:
            sheet.used_range.columns.autofit()
            # sheet.used_range.wrap_text = True


def decide_row_height_column_width(wb: xw.Book) -> None:
    "Decide row height and column width based on data"
    for sheet in wb.sheets:
        df = pd.DataFrame(sheet.range("A1").expand().value)
        df.apply(lambda x: x.astype(str).str.len().max(), axis=0)


if __name__ == "__main__":
    pass
