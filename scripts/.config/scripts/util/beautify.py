"For beautifying excel files based on given template"

from pathlib import Path
import click
import xlwings as xw
from . import excelx

TEMPLATES = [
    "Arial, Size 12",
    "Arial, Size 11",
    "Arial, Size 10",
    "Aptos, Size 12",
    "Aptos, Size 11",
    "Aptos, Size 10",
    "Aptos Narrow, Size 12",
    "Aptos Narrow, Size 11",
    "Aptos Narrow, Size 10",
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
    "--width",
    is_flag=True,
    help="Apply smart width only, skip font formatting (based on content, max 80 chars, word wrap)",
)
@click.option(
    "-f",
    "--font-only",
    is_flag=True,
    help="Apply font/size only, skip smart width (sheet view is always reset)",
)
def beautify(xl_file: str, width: bool, font_only: bool) -> None:
    """
    Beautify excel file.

    By default, shows a font template menu first (default: Arial Size 11, or
    select 0 to keep the current font/size), resets sheet view to Normal, then
    applies smart width. Use -w to skip the font prompt entirely and apply smart
    width only. Use -f to apply font/size only, skipping smart width.
    """
    if width and font_only:
        raise click.UsageError("-w and -f cannot be used together.")

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

    # Font choice comes first, before any other formatting. -w skips it entirely.
    if not width:
        click.echo("Available font templates:")
        click.echo("  0: Keep current font/size (no change)")
        for idx, tmpl in enumerate(TEMPLATES, start=1):
            click.echo(f"  {idx}: {tmpl}")
        while True:
            choice = click.prompt(
                "Select template number (Enter for default, 0 to keep unchanged)",
                default="2",
            )
            try:
                template_idx = int(choice)
                if 0 <= template_idx <= len(TEMPLATES):
                    break
            except ValueError:
                pass
            click.echo(f"Please enter a number between 0 and {len(TEMPLATES)}")

        if template_idx == 0:
            click.echo("Keeping current font and size.")
        else:
            template = TEMPLATES[template_idx - 1]
            parts = template.rsplit(", Size ", 1)
            font_name = parts[0]
            font_size = int(parts[1])
            excelx.set_format(wb, font_name=font_name, font_size=font_size)
            click.echo(f"Applied font: {template}")

    # Sheet view always resets to Normal; smart width is skipped for -f
    excelx.set_normal_view(wb)
    if not font_only:
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
