"For beautifying excel files based on given template"

from pathlib import Path
import click
import xlwings as xw
from . import excelx

TEMPLATES = [
    "Aptos, Size 12",
    "Aptos, Size 11",
    "Aptos, Size 10",
    "Aptos Narrow, Size 12",
    "Aptos Narrow, Size 11",
    "Aptos Narrow, Size 10",
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
    "-f",
    "--font",
    is_flag=True,
    help="Apply font formatting only (shows template menu, default: Aptos Narrow Size 11)",
)
def beautify(xl_file: str, font: bool) -> None:
    """
    Beautify excel file.

    By default, applies smart width (based on content, max 80 chars, word wrap).
    Use -f to apply font formatting only (no smart width).
    """
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

    wb = get_wb(xl_file)
    if wb is None:
        return

    # Apply font formatting if -f flag is used
    if font:
        click.echo("Available font templates:")
        for idx, tmpl in enumerate(TEMPLATES, start=1):
            click.echo(f"  {idx}: {tmpl}")
        while True:
            choice = click.prompt(
                "Select template number (Enter for default)", default="2"
            )
            try:
                template_idx = int(choice)
                if 1 <= template_idx <= len(TEMPLATES):
                    break
            except ValueError:
                pass
            click.echo(f"Please enter a number between 1 and {len(TEMPLATES)}")

        template = TEMPLATES[template_idx - 1]
        parts = template.rsplit(", Size ", 1)
        font_name = parts[0]
        font_size = int(parts[1])
        excelx.set_format(wb, font_name=font_name, font_size=font_size)
        click.echo(f"Applied font: {template}")
    else:
        # Apply smart width only when -f flag is not used
        excelx.set_column_width_by_content(wb)

    click.echo(f"Done. Please review and save {wb.name} manually.")


def get_wb(file_name: str) -> xw.Book | None:
    """
    Get workbook by name or active workbook.
    Uses wb.name instead of wb.fullname to avoid hanging on SharePoint/OneDrive files.
    """
    try:
        if file_name == "current workbook":
            wb = xw.apps.active.books.active  # type: ignore
        else:
            wb = xw.App(visible=False).books.open(file_name)
        # Use wb.name instead of wb.fullname - fullname can hang for SharePoint URLs
        if wb.name:
            return wb
    except Exception:
        click.echo("File not found.")
    return None


if __name__ == "__main__":
    beautify()
