"Utilities for managing excel files"

import click
from pathlib import Path
from decouple import config
from datetime import date

import xlwings as xw

# Legacy
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
    pass


if __name__ == "__main__":
    pass
