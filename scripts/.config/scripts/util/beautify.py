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
@click.option(
    "-w",
    "--smart-width",
    is_flag=True,
    help="Set column width based on content (max 80 chars, word wrap)",
)
def beautify(xl_file: str, smart_width: bool) -> None:
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

    # Parse template string: "Font Name, Size N"
    template = templates[template_number]
    parts = template.rsplit(", Size ", 1)
    if len(parts) != 2:
        click.echo("Invalid template format.")
        return
    font_name = parts[0]
    font_size = int(parts[1])

    wb = get_wb(xl_file)
    if wb is None:
        return

    excelx.set_format(wb, font_name=font_name, font_size=font_size)

    if smart_width:
        excelx.set_column_width_by_content(wb)

    wb.save()
    click.echo(f"Saved {wb.fullname}")


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
