"For beautifying excel files based on given template"

from pathlib import Path
import click
import xlwings as xw
from . import excelx

TEMPLATE = [
    "Arial, Size 12",
    "Arial, Size 11",
    "Arial, Size 10",
    "Calibri, Size 11",
    "Calibri, Size 10",
    "Helvetica, Size 12",
    "Helvetica, Size 11",
    "Tahoma, Size 11",
    "Tahoma, Size 10",
    "Times New Roman, Size 11",
]


@click.command()
@click.argument("xl_file", default="")
@click.option("-a", "--autofit", is_flag=True, help="Auto fit columns")
def beautify(xl_file: str, autofit: bool) -> None:
    "Beautify excel file based on template."
    while True:
        if xl_file == "":
            xl_file = click.prompt(
                "The file name in the current directory, leave empty to use",
                default="current workbook",
            )
        if Path(xl_file).is_file() and Path(xl_file).suffix in [
            ".xls",
            ".xlsx",
            ".xlsm",
        ]:
            break
        else:
            # If default, try current workbook
            if get_wb(xl_file):
                break
            else:
                click.echo("No active excel workbook or file found.")
                return
    click.echo("The following options are available:")
    templates = {index: value for index, value in enumerate(TEMPLATE, start=1)}
    for index, template in templates.items():
        click.echo(f"{index}: {template}")
    while True:
        template_number = click.prompt("Type the template number or q to quit")
        try:
            if int(template_number) in templates.keys():
                template_number = int(template_number)
                break
        except ValueError:
            if template_number.lower() == "q":
                return
        click.echo("Not a valid value.")
    match templates[template_number]:
        case "Arial, Size 12":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(wb, font_name="Arial", font_size=12, autofit=autofit)
        case "Arial, Size 11":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(wb, font_name="Arial", font_size=11, autofit=autofit)
        case "Arial, Size 10":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(wb, font_name="Arial", font_size=10, autofit=autofit)
        case "Calibri, Size 11":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(
                    wb, font_name="Calibri", font_size=11, autofit=autofit
                )
        case "Calibri, Size 10":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(
                    wb, font_name="Calibri", font_size=10, autofit=autofit
                )
        case "Tahoma, Size 11":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(wb, font_name="Tahoma", font_size=11, autofit=autofit)
        case "Tahoma, Size 10":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(wb, font_name="Tahoma", font_size=10, autofit=autofit)
        case "Helvetica, Size 12":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(
                    wb, font_name="Helvetica", font_size=12, autofit=autofit
                )
        case "Helvetica, Size 11":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(
                    wb, font_name="Helvetica", font_size=11, autofit=autofit
                )
        case "Times New Roman, Size 11":
            wb = get_wb(xl_file)
            if wb is not None:
                excelx.set_format(
                    wb, font_name="Times New Roman", font_size=11, autofit=autofit
                )
        case _:
            click.echo("Invalid option.")


def get_wb(file_name: str) -> xw.Book | None:
    try:
        if file_name == "current workbook":
            wb = xw.apps.active.books.active  # type: ignore
        else:
            wb = xw.App(visible=False).books.open(file_name)
        try:
            if wb.fullname:
                return wb
        except Exception:
            return
    except Exception:
        click.echo("File not found.")


if __name__ == "__main__":
    beautify()
