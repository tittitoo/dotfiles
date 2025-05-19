import click
import pypdf
import os
import re
import logging
from pathlib import Path
from pypdf.errors import FileNotDecryptedError

from reportlab.pdfgen import canvas

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import blue

ACRONYMS = [
    "BR",
    "CERT",
    "DR",
    "DS",
    "IOM",
    "PR",
    "PL",
    "PIC",
    "PTT",
    "REG",
    "TD",
    "TQ",
]

# Set logging level for pypdf so that warnings are not printed
logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)


@click.command()
@click.option("-o", "--outline", is_flag=True, help="Add outline to file from filename")
@click.option("-y", "--yes", is_flag=True, help="Answer yes to the current directory")
@click.option(
    "-t", "--toc", is_flag=True, help="Add table of contends in separate page"
)
def combine_pdf(outline: bool, toc: bool, yes: bool):
    """
    Combine pdf and output result pdf in the current folder.
    If the combined file already exists, it will remove it first and re-combine.
    """
    if not yes:
        click.confirm(
            "The command will merge all the pdf in the current directory", abort=True
        )
    directory = Path.cwd()
    filename = "00-Combined.pdf"
    if os.path.exists(directory / filename):
        try:
            os.remove(directory / filename)
        except PermissionError:
            click.echo(f"Cannot remove {filename}. Please close the file first.")

    # List pdf files
    pdf_files = [
        f for f in os.listdir(directory) if f.endswith("pdf") or f.endswith("PDF")
    ]

    # Sort the PDF files alphabetically
    pdf_files.sort()

    # Creat a PdfMerger object
    writer = pypdf.PdfWriter()

    encrypted_files: list[str] = []
    # Add all the PDF files to the merger
    try:
        for pdf_file in pdf_files:
            file_path = os.path.join(directory, pdf_file)
            try:
                # Read for side effect to see if it is encrypted
                pypdf.PdfReader(file_path)
                if outline:
                    add_outline(Path(file_path))
                writer.append(file_path)
            except FileNotDecryptedError:
                encrypted_files.append(pdf_file)
            except Exception as e:
                click.echo(f"Encountered this error {e}")
    except Exception as e:
        click.echo(f"Encountered this error {e}")

    # Write the ouput to a new PDF file
    output_path = os.path.join(directory, filename)
    try:
        with open(output_path, "wb") as f:
            writer.write(f)
            if encrypted_files:
                click.echo(
                    "The following files are encrypted and not included in combined file."
                )
                for index, item in enumerate(encrypted_files):
                    click.echo(
                        f"{index + 1}: {item}"
                    )  # Print the file name with index (item)
            successful_pdf_files = list(set(pdf_files) - set(encrypted_files))
            if successful_pdf_files:
                click.echo(
                    f"Combined following {len(successful_pdf_files)} files into '{filename}'"
                )
                successful_pdf_files.sort()
                for index, item in enumerate(successful_pdf_files):
                    click.echo(
                        f"{index + 1}: {item}"
                    )  # Print the file name with index (item)
        if toc:
            # TODO: Add code to add toc
            click.echo("Still in implementation stage")
            # toc_list = find_toc(Path(output_path))
            # make_toc("00-toc.pdf", toc_list)

    except Exception as e:
        click.echo(f"Encountered this error {e}")
    # Close the writer
    writer.close()


def add_outline(file_path: Path):
    """
    Add pdf outline from fileame
    Take in filename, put this as pdf outline, and rewrite file with same name.
    """
    try:
        reader = pypdf.PdfReader(file_path)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        # Clear outline first
        writer.outline.clear()
        # Clean file name
        # Remove leading number such as 2, 02, 002 etc
        filename = re.sub(r"^\b0*[1-9]\d*\b|\b0+\b|\b0\b", "", filename)
        # Remove word from acronums at the start of sentence
        pattern = r"^\s*(" + "|".join(re.escape(word) for word in ACRONYMS) + r")\b\s*"
        filename = re.sub(pattern, "", filename, 1)
        # Remove any leading or trailing spaces
        filename = filename.strip()
        # Add outline
        writer.add_outline_item(filename, 0)
        with open(file_path, "wb") as f:
            writer.write(f)
        click.echo(f"Outline added to {filename}")
    except Exception as e:
        click.echo(f"Encountered this error {e} for some files.")


def find_toc(file_path: Path) -> list[str] | None:
    """
    Add toc in a separate page
    """
    try:
        reader = pypdf.PdfReader(file_path)
        outline = reader.outline

        if not outline:
            click.echo("PDF has no outline")
            return
        # # Create TOC page content
        toc_lines = []

        def process_outline(outline_items, level=0):
            for item in outline_items:
                if isinstance(item, list):
                    process_outline(item, level + 1)
                else:
                    title = item.title
                    page_number = reader.get_destination_page_number(item)
                    # indent = "   " * level
                    toc_lines.append((title, page_number))

        process_outline(outline)
        for line in toc_lines:
            click.echo(line)
        return toc_lines
        # toc_content = "\n".join(toc_lines)

        # # Create a new page for toc
        # toc_page = writer.add_blank_page(
        #     width=reader.pages[0].mediabox.width, height=reader.pages[0].mediabox.height
        # )
        # y = toc_page.mediabox.height - 50
        # annotation = FreeText(
        #     rect=(50, y, 500, y + 20),
        #     text="Table of Contents",
        #     font="Helvetica-Bold",
        # )
        # writer.add_annotation(page_number=0, annotation=annotation)
        #
        # y -= 30
        # for line in toc_lines:
        #     annotation = FreeText(
        #         rect=(75, y, 500, y + 12),
        #         text=line,
        #         font="Helvetica",
        #         font_size="10pt",
        #         border_color="ffffff",
        #     )
        #     writer.add_annotation(page_number=0, annotation=annotation)
        #     y -= 15
        #
        # # writer.insert_page(toc_page, 0)
        #
        # # toc_page.add_text(
        # #     "Table of Contents",
        # #     50,
        # #     toc_page.mediabox.width / 2,
        # #     toc_page.mediabox.height - 50,
        # #     align="center",
        # #     font="Helvetica-Bold",
        # #     fontsize=20,
        # # )
        # # y = toc_page.mediabox.height - 100
        # # for line in toc_lines:
        # #     toc_page.add_text(
        # #         line,
        # #         50,
        # #         toc_page.mediabox.width / 2,
        # #         y,
        # #         align="center",
        # #         font="Helvetica",
        # #         fontsize=12,
        # #     )
        # #     y -= 20
        # #
        # # # Add the toc page to the writer
        # # writer.add_page(toc_page, 0)
        # #
        # # Add all other pages from the original PDF
        # for page in reader.pages:
        #     writer.add_page(page)
        #
        # # Write the updated PDF file
        # with open(file_path, "wb") as f:
        #     writer.write(f)
        # click.echo(f"TOC added to {file_path}")

    except Exception as e:
        click.echo(f"Encountered this error {e}.")


def make_toc(output_pdf, outline_data):
    """
    Generates a PDF with a clickable table of contents using reportlab.

    Args:
        output_pdf (str): Path to the output PDF.
        outline_data (list): A list of tuples, where each tuple is (title, page_number).
    """

    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.textColor = blue

    elements = []
    destinations = []
    y_position = 700

    for title, page_number in outline_data:
        link_id = f"page_{page_number}"
        destinations.append((link_id, page_number - 1))
        text = f'<a href="#{link_id}">{title}</a>'
        p = Paragraph(text, normal_style)
        elements.append(p)

        temp_canvas = canvas.Canvas("temp.pdf")
        p.wrapOn(temp_canvas, 6 * inch, 1 * inch)
        height = p.height

        y_position -= height + 5

    def add_destinations(canvas, doc):
        for dest_id, page_num in destinations:
            canvas.bookmarkPage(dest_id, page_num)
            canvas.addOutlineEntry(
                dest_id, dest_id, level=0, actionType="GoTo", targetPageNum=page_num + 1
            )  # add outline entry

    doc.build(elements, onFirstPage=add_destinations, onLaterPages=add_destinations)


if __name__ == "__main__":
    pass
