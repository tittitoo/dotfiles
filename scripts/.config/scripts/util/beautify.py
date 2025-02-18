"For beautifying excel files based on given template"

from pathlib import Path
import click
import xlwings as xw
from . import excelx

TEMPLATE = [
    "Auto",
    "MODEC Commissioning Spares",
    "MODEC 2YRS Spares",
    "Seatrium CQ Form",
]


@click.command()
@click.argument("xl_file", default="")
def beautify(xl_file: str):
    "Beautify excel file based on template."
    while True:
        if xl_file == "":
            xl_file = click.prompt(
                "The file name in the current directory, leave empty to use current workbook",
                default="",
            )
        if Path(xl_file).is_file() and Path(xl_file).suffix in [
            ".xls",
            ".xlsx",
            ".xlsm",
        ]:
            break
        else:
            # If string is empty, try current workbook
            break
            # click.echo("Requires an excel file in current directory.")
            # xl_file = click.prompt("The file name in the current directory")
    click.echo("The following templates are available:")
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
        case "Auto":
            click.echo("Auto")
            auto(xl_file)
        case "MODEC Commissioning Spares":
            click.echo("MODEC Commissioning Spares")
        case "MODEC 2YRS Spares":
            click.echo("MODEC 2YRS Spares")
        case "Seatrium CQ Form":
            click.echo("Seatrium CQ Form")
        case _:
            click.echo("Invalid template")


def auto(file_name: str):
    "Auto beautify excel file based on template."
    try:
        if file_name == "":
            wb = xw.apps.active.books.active  # type: ignore
        else:
            wb = xw.App(visible=False).books.open(file_name)
        click.echo(f"{wb.fullname}")
        excelx.set_font(wb, font_name="Tahoma", font_size=11)
        # excelx.decide_row_height_column_width(wb)
        # wb.save()
    except Exception:
        click.echo("File not found.")


if __name__ == "__main__":
    beautify()
