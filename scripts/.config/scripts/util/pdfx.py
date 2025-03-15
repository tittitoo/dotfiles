import click
import pypdf
import os
from pathlib import Path


@click.command()
@click.option("-o", "--outline", is_flag=True, help="Add outline to file from filename")
@click.option(
    "-t", "--toc", is_flag=True, help="Add table of contends in separate page"
)
def combine_pdf(outline: bool, toc: bool):
    """
    Combine pdf and output result pdf in the current folder.
    If the combined file already exists, it will remove it first and re-combine.
    """
    directory = click.prompt(
        "The command will merge all the pdf in the current directory: 'Enter' to accept, 'Ctrl+c' to abort",
        default=Path.cwd(),
        show_default=False,
    )
    directory = Path(directory)
    filename = "00-Combined.pdf"
    if os.path.exists(directory / filename):
        os.remove(directory / filename)

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
            except Exception:
                encrypted_files.append(pdf_file)
    except Exception:
        pass

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
            add_toc(Path(output_path))
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
        # Add outline
        writer.add_outline_item(filename, 0)
        with open(file_path, "wb") as f:
            writer.write(f)
        click.echo(f"Outline added to {filename}")
    except Exception as e:
        click.echo(f"Encountered this error {e} for some files.")


def add_toc(file_path: Path):
    """
    Add toc in a separate page
    """
    pass


if __name__ == "__main__":
    pass
