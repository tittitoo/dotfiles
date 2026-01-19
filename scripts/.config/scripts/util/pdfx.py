import click
import pypdf
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
)
import os
import re
import logging
import tempfile
from pathlib import Path
from pypdf.errors import FileNotDecryptedError

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def is_cover_file(filename: str) -> bool:
    """
    Check if a file is a cover file.
    Matches any PDF file containing 'cover' in the filename (case-insensitive).
    """
    name_lower = filename.lower()
    return name_lower.endswith(".pdf") and "cover" in name_lower


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


def find_manifest_file(directory: Path) -> Path | None:
    """
    Find a manifest file (md or txt) in the directory.
    Markdown files take precedence over txt files.
    If multiple files of same type exist, prompt user to choose.
    """
    md_files = list(directory.glob("*.md"))
    txt_files = list(directory.glob("*.txt"))

    # Markdown takes precedence
    if md_files:
        candidates = md_files
    elif txt_files:
        candidates = txt_files
    else:
        click.echo("Error: No manifest file (.md or .txt) found in current directory")
        return None

    if len(candidates) == 1:
        return candidates[0]

    # Multiple files found - let user choose
    click.echo("Multiple manifest files found:")
    for i, f in enumerate(candidates, 1):
        click.echo(f"  {i}. {f.name}")

    while True:
        choice = click.prompt("Select file number", type=int)
        if 1 <= choice <= len(candidates):
            return candidates[choice - 1]
        click.echo(f"Please enter a number between 1 and {len(candidates)}")


def resolve_pdf_file(directory: Path, name: str) -> str | None:
    """
    Try to find a PDF file matching the given name.

    Tries in order:
    1. Exact match (name as-is)
    2. With .pdf extension added
    3. Case-insensitive search for similar names

    Args:
        directory: Directory to search in
        name: Filename or potential filename (with or without .pdf)

    Returns:
        The actual filename if found, None otherwise.
    """
    # Try exact match first
    if (directory / name).exists():
        return name

    # Try adding .pdf extension
    name_with_pdf = name if name.lower().endswith(".pdf") else f"{name}.pdf"
    if (directory / name_with_pdf).exists():
        return name_with_pdf

    # Try case-insensitive search
    name_lower = name_with_pdf.lower()
    for f in directory.iterdir():
        if f.is_file() and f.name.lower() == name_lower:
            return f.name

    return None


def parse_manifest_file(
    file_path: Path,
    directory: Path | None = None,
) -> tuple[str, list[str], list[dict]] | None:
    """
    Parse a markdown/txt manifest file for PDF combining with hierarchical outline.

    Expected format:
        # Output Filename

        ## Section Title
        - file1
        - file2.pdf

        ### Subsection Title
        - file3

        ## Section With File section.pdf
        - file4

    Heading levels:
    - # Title: Output filename (required)
    - ## Section: Level 1 heading (can be a PDF filename)
    - ### Subsection: Level 2 heading
    - #### Sub-subsection: Level 3 heading (and so on)

    All headings and list items are treated as potential PDF filenames.
    The .pdf extension is optional - files will be matched with or without it.
    Files that cannot be found are skipped and logged.

    Args:
        file_path: Path to the manifest file
        directory: Directory to search for PDF files (defaults to manifest's directory)

    Returns:
        Tuple of (output_filename, list_of_pdf_files, outline_structure) or None.
        outline_structure is a list of dicts with recursive children:
        [
            {
                "title": "Section Title",
                "level": 1,
                "file": None or "section.pdf",
                "children": [
                    {"title": "Subsection", "level": 2, "file": None, "children": [...]},
                    ...
                ]
            },
            ...
        ]
    """
    if directory is None:
        directory = file_path.parent

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.strip().split("\n")
        title = None
        pdf_files = []
        outline_structure = []
        not_found_files = []

        # Stack to track parent sections at each level
        # level_stack[i] contains the section dict for heading level i+1 (## = level 1)
        level_stack: list[dict | None] = [None] * 10  # Support up to 10 levels

        def try_resolve_file(name: str) -> str | None:
            """Try to resolve a potential filename, log if not found."""
            resolved = resolve_pdf_file(directory, name)
            if resolved is None:
                not_found_files.append(name)
            return resolved

        def parse_heading_line(line: str) -> tuple[int, str, str | None]:
            """
            Parse a heading line to extract level, title, and optional file.
            Returns (level, title, resolved_file_or_none).
            Level 1 = ##, Level 2 = ###, etc.

            The heading text itself is treated as a potential filename.
            """
            # Count # characters
            hash_count = 0
            for char in line:
                if char == "#":
                    hash_count += 1
                else:
                    break

            # Level is hash_count - 1 (## = level 1, ### = level 2, etc.)
            level = hash_count - 1
            heading_text = line[hash_count:].strip()

            # Try to parse as "Title filename" or just "filename"
            heading_file = None
            heading_title = heading_text

            # First, try the whole heading as a filename
            resolved_whole = resolve_pdf_file(directory, heading_text)
            if resolved_whole:
                heading_file = resolved_whole
                # Use the text without .pdf as title
                heading_title = os.path.splitext(heading_text)[0]
                if heading_title.lower().endswith(".pdf"):
                    heading_title = heading_title[:-4]
                return level, heading_title, heading_file

            # Try splitting: "Title filename" where filename is the last word
            parts = heading_text.rsplit(" ", 1)
            if len(parts) == 2:
                potential_file = parts[1]
                resolved = resolve_pdf_file(directory, potential_file)
                if resolved:
                    heading_title = parts[0]
                    heading_file = resolved
                    return level, heading_title, heading_file

            # No file found - this is just a section title
            return level, heading_title, None

        def find_parent_for_level(level: int) -> dict | None:
            """Find the appropriate parent section for a given level."""
            # Look for the nearest parent at a higher level (lower number)
            for i in range(level - 1, 0, -1):
                if level_stack[i] is not None:
                    return level_stack[i]
            return None

        for line in lines:
            stripped = line.strip()

            # Parse main title (# Title) - exactly one #
            if stripped.startswith("# ") and not stripped.startswith("## "):
                title = stripped[2:].strip()

            # Parse heading (## or more)
            elif stripped.startswith("## "):
                level, heading_title, heading_file = parse_heading_line(stripped)

                if heading_file:
                    pdf_files.append(heading_file)

                new_section = {
                    "title": heading_title,
                    "level": level,
                    "file": heading_file,
                    "children": [],
                }

                # Find parent and add to appropriate place
                parent = find_parent_for_level(level)
                if parent is not None:
                    parent["children"].append(new_section)
                else:
                    # Top-level section
                    outline_structure.append(new_section)

                # Update level stack
                level_stack[level] = new_section
                # Clear lower levels (they're no longer current)
                for i in range(level + 1, len(level_stack)):
                    level_stack[i] = None

            # Parse list items (- filename)
            elif stripped.startswith("- "):
                item_text = stripped[2:].strip()
                if item_text:
                    # Try to resolve as a PDF file
                    resolved_file = try_resolve_file(item_text)

                    if resolved_file:
                        pdf_files.append(resolved_file)

                        # Find the current parent (most recent heading at any level)
                        parent = None
                        for i in range(len(level_stack) - 1, 0, -1):
                            if level_stack[i] is not None:
                                parent = level_stack[i]
                                break

                        if parent is not None:
                            # Add as a child entry (with level one deeper than parent)
                            child_entry = {
                                "title": None,  # Will use cleaned filename
                                "level": parent["level"] + 1,
                                "file": resolved_file,
                                "children": [],
                            }
                            parent["children"].append(child_entry)
                        else:
                            # No parent, create implicit root section
                            child_entry = {
                                "title": None,
                                "level": 1,
                                "file": resolved_file,
                                "children": [],
                            }
                            outline_structure.append(child_entry)

        # Log files that couldn't be found
        if not_found_files:
            click.echo(
                "Warning: The following items could not be matched to PDF files:"
            )
            for f in not_found_files:
                click.echo(f"  - {f}")

        if not title:
            click.echo("Error: No title found in manifest file (expected '# Title')")
            return None

        if not pdf_files:
            click.echo("Error: No PDF files found from manifest entries")
            return None

        # Add .pdf extension to title if not present
        output_filename = title if title.lower().endswith(".pdf") else f"{title}.pdf"

        return output_filename, pdf_files, outline_structure

    except Exception as e:
        click.echo(f"Error reading manifest file: {e}")
        return None


@click.command()
@click.option("-o", "--outline", is_flag=True, help="Add outline to file from filename")
@click.option("-y", "--yes", is_flag=True, help="Answer yes to the current directory")
@click.option(
    "-t", "--toc", is_flag=True, help="Add table of contends in separate page"
)
@click.option(
    "-m",
    "--manifest",
    "use_manifest",
    is_flag=True,
    help="Use manifest file (md/txt) specifying output name and files to combine",
)
def combine_pdf(outline: bool, toc: bool, yes: bool, use_manifest: bool):
    """
    Combine pdf and output result pdf in the current folder.
    If the combined file already exists, it will remove it first and re-combine.

    With --manifest flag, reads a manifest file (md/txt) where:
    - The '# Title' becomes the output filename
    - '## Section' creates level 1 outline (links to first child if no file)
    - '## Section file.pdf' creates level 1 outline with that file
    - '- file.pdf' items become level 2 outline entries
    """
    if not yes:
        click.confirm(
            "The command will merge the pdf in the current directory", abort=True
        )
    directory = Path.cwd()

    outline_structure = None  # For manifest mode

    # Use manifest file if --manifest flag is set
    if use_manifest:
        manifest_path = find_manifest_file(directory)
        if manifest_path is None:
            return

        click.echo(f"Using manifest: {manifest_path.name}")
        result = parse_manifest_file(manifest_path, directory)
        if result is None:
            return
        filename, pdf_files, outline_structure = result

        # Files are already resolved and validated during parsing
        # Missing files are logged as warnings and skipped
    else:
        filename = "00-Combined.pdf"

        # List pdf files
        pdf_files = [
            f for f in os.listdir(directory) if f.endswith("pdf") or f.endswith("PDF")
        ]

        # Sort the PDF files alphabetically
        pdf_files.sort()

        # Check for multiple cover files
        cover_files = [f for f in pdf_files if is_cover_file(f)]
        if len(cover_files) > 1:
            click.echo("Error: Multiple cover files found:")
            for f in cover_files:
                click.echo(f"  - {f}")
            click.echo("Please ensure only one file contains 'cover' in the filename.")
            return

        # Ensure cover file is first (regardless of alphabetical order)
        if cover_files:
            cover_file = cover_files[0]
            pdf_files.remove(cover_file)
            pdf_files.insert(0, cover_file)

    # Remove existing output file if present
    if os.path.exists(directory / filename):
        try:
            os.remove(directory / filename)
        except PermissionError:
            click.echo(f"Cannot remove {filename}. Please close the file first.")
            return

    # Create a PdfWriter object
    writer = pypdf.PdfWriter()

    encrypted_files: list[str] = []
    file_page_starts: dict[str, int] = {}  # Track start page for each file
    current_page = 0

    # Add all the PDF files to the merger
    try:
        for pdf_file in pdf_files:
            file_path = os.path.join(directory, pdf_file)
            is_cover = is_cover_file(pdf_file)
            try:
                # Read to check encryption and get page count
                reader = pypdf.PdfReader(file_path)
                page_count = len(reader.pages)

                # Track where this file starts
                file_page_starts[pdf_file] = current_page

                if outline and not is_cover and not use_manifest:
                    # Add outline to non-cover files only (non-manifest mode)
                    add_outline(Path(file_path))
                elif is_cover:
                    # Clear any existing outline from cover file
                    clear_outline(Path(file_path))
                writer.append(file_path)
                current_page += page_count
            except FileNotDecryptedError:
                encrypted_files.append(pdf_file)
            except Exception as e:
                click.echo(f"Encountered this error {e}")
    except Exception as e:
        click.echo(f"Encountered this error {e}")

    # Write the output to a new PDF file
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
                # Preserve order from pdf_files for display
                ordered_successful = [f for f in pdf_files if f in successful_pdf_files]
                for index, item in enumerate(ordered_successful):
                    click.echo(f"{index + 1}: {item}")

        # Add hierarchical outline for manifest mode
        if use_manifest and outline_structure:
            add_hierarchical_outline(
                Path(output_path), outline_structure, file_page_starts
            )

        if toc:
            # Check if cover page exists
            has_cover = any(is_cover_file(f) for f in successful_pdf_files)
            if use_manifest and outline_structure:
                # Filter out cover files from file_page_starts for TOC
                # Cover pages should not appear in TOC
                toc_file_page_starts = {
                    f: p for f, p in file_page_starts.items() if not is_cover_file(f)
                }
                # Use hierarchical TOC for manifest mode
                add_toc_to_pdf(
                    Path(output_path),
                    has_cover=has_cover,
                    outline_structure=outline_structure,
                    file_page_starts=toc_file_page_starts,
                )
            else:
                add_toc_to_pdf(Path(output_path), has_cover=has_cover)

    except Exception as e:
        click.echo(f"Encountered this error {e}")
    # Close the writer
    writer.close()


def clean_outline_title(filename: str) -> str:
    """
    Clean a filename to create a nice outline title.
    Removes leading numbers and common acronyms.
    """
    # Remove .pdf extension
    title = os.path.splitext(filename)[0]
    # Remove leading number such as 2, 02, 002 etc
    title = re.sub(r"^\b0*[1-9]\d*\b|\b0+\b|\b0\b", "", title)
    # Remove word from acronyms at the start of sentence
    pattern = r"^\s*(" + "|".join(re.escape(word) for word in ACRONYMS) + r")\b\s*"
    title = re.sub(pattern, "", title, 1)
    # Remove any leading or trailing spaces
    return title.strip()


def add_hierarchical_outline(
    file_path: Path,
    outline_structure: list[dict],
    file_page_starts: dict[str, int],
) -> None:
    """
    Add hierarchical outline to a PDF based on manifest structure.

    Args:
        file_path: Path to the combined PDF
        outline_structure: List of section dicts from parse_manifest_file
                          Each dict has: title, level, file, children (recursive)
        file_page_starts: Dict mapping filename to starting page number (0-indexed)
    """
    try:
        reader = pypdf.PdfReader(file_path)
        writer = pypdf.PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Clear existing outline
        writer.outline.clear()

        def get_first_file_page(item: dict) -> int | None:
            """Recursively find the first file's page in an item and its children."""
            file = item.get("file")
            if file and file in file_page_starts:
                return file_page_starts[file]
            for child in item.get("children", []):
                page = get_first_file_page(child)
                if page is not None:
                    return page
            return None

        def add_outline_items(items: list[dict], parent=None):
            """Recursively add outline items."""
            for item in items:
                title = item.get("title")
                file = item.get("file")
                children = item.get("children", [])

                # Determine page for this item
                if file and file in file_page_starts:
                    page = file_page_starts[file]
                else:
                    page = get_first_file_page(item)

                if page is None:
                    continue  # Skip if no valid page

                # Use title or cleaned filename
                display_title = (
                    title if title else (clean_outline_title(file) if file else None)
                )

                if display_title:
                    outline_item = writer.add_outline_item(
                        display_title, page, parent=parent
                    )
                    # Recursively add children
                    if children:
                        add_outline_items(children, parent=outline_item)

        add_outline_items(outline_structure)

        # Write back
        with open(file_path, "wb") as f:
            writer.write(f)

        click.echo(f"Added hierarchical outline to {file_path.name}")

    except Exception as e:
        click.echo(f"Error adding hierarchical outline: {e}")


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
        # Remove word from acronyms at the start of sentence
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


def clear_outline(file_path: Path):
    """
    Clear any existing outline from a PDF file.
    Used to ensure cover pages don't have outline entries.
    """
    try:
        reader = pypdf.PdfReader(file_path)
        # Check if there's an outline to clear
        if not reader.outline:
            return

        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.outline.clear()
        with open(file_path, "wb") as f:
            writer.write(f)
    except Exception:
        pass  # Silently ignore errors for cover files


def get_outline_data(file_path: Path) -> list[tuple[str, int]]:
    """
    Extract outline data from a PDF file.

    Returns:
        List of (title, page_number) tuples where page_number is 0-indexed.
    """
    toc_lines = []
    try:
        reader = pypdf.PdfReader(file_path)
        outline = reader.outline

        if not outline:
            return toc_lines

        def process_outline(outline_items, level=0):
            for item in outline_items:
                if isinstance(item, list):
                    process_outline(item, level + 1)
                else:
                    title = item.title
                    page_number = reader.get_destination_page_number(item)
                    toc_lines.append((title, page_number))

        process_outline(outline)
    except Exception as e:
        click.echo(f"Error reading outline: {e}")

    return toc_lines


def _register_arial_font() -> str:
    """
    Register Arial font for reportlab. Returns the font name to use.
    Falls back to Helvetica if Arial is not available.
    """
    # Common Arial font paths
    arial_paths = [
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        # Mac
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/usr/share/fonts/TTF/arial.ttf",
    ]

    for path in arial_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("Arial", path))
                return "Arial"
            except Exception:
                continue

    # Fallback to Helvetica (built-in, similar to Arial)
    return "Helvetica"


def create_toc_pdf(
    toc_data: list[tuple[str, int]],
    output_path: str,
    toc_page_count: int,
    page_size=A4,
    cover_pages: int = 0,
) -> tuple[int, list[dict]]:
    """
    Create a PDF with table of contents (visual only, links added later).

    Args:
        toc_data: List of (title, page_number) tuples (0-indexed page numbers)
        output_path: Path for the TOC PDF
        toc_page_count: Number of TOC pages (for adjusting target page numbers)
        page_size: Page size (default A4)
        cover_pages: Number of cover pages that precede TOC in final PDF

    Returns:
        Tuple of (number of pages created, list of link info dicts)
    """
    font_name = _register_arial_font()

    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size

    # Margins and layout
    left_margin = 50
    right_margin = width - 50
    top_margin = height - 50
    bottom_margin = 60
    line_height = 20
    title_font_size = 16
    entry_font_size = 11

    pages_created = 0
    link_info = []  # Store link positions for later

    def start_new_page(is_first=False):
        nonlocal pages_created
        if not is_first:
            c.showPage()
        pages_created += 1

        # Draw title on each page
        if font_name == "Helvetica":
            c.setFont("Helvetica-Bold", title_font_size)
        else:
            c.setFont(font_name, title_font_size)
        c.drawString(left_margin, top_margin, "Table of Contents")

        return top_margin - 35  # Return starting y position for entries

    y = start_new_page(is_first=True)
    c.setFont(font_name, entry_font_size)

    for title, original_page_num in toc_data:
        if y < bottom_margin:
            y = start_new_page()
            c.setFont(font_name, entry_font_size)

        # Target page in final PDF:
        # cover_pages + toc_page_count + (original_page_num - cover_pages)
        # = original_page_num + toc_page_count
        target_page = original_page_num + toc_page_count

        # Display page number (1-indexed for human readability)
        display_page = target_page + 1

        # Draw title in dark blue
        c.setFillColorRGB(0, 0, 0.8)
        c.drawString(left_margin, y, title)

        # Draw page number (right-aligned) in black
        c.setFillColorRGB(0, 0, 0)
        c.drawRightString(right_margin, y, str(display_page))

        # Draw dotted line between title and page number
        title_width = c.stringWidth(title, font_name, entry_font_size)
        page_width = c.stringWidth(str(display_page), font_name, entry_font_size)
        dot_start = left_margin + title_width + 10
        dot_end = right_margin - page_width - 10

        if dot_end > dot_start:
            c.setFillColorRGB(0.5, 0.5, 0.5)  # Gray dots
            dot_x = dot_start
            while dot_x < dot_end:
                c.drawString(dot_x, y, ".")
                dot_x += 5

        # Store link info for adding via pypdf later
        link_info.append(
            {
                "toc_page": pages_created - 1,  # 0-indexed within TOC
                "rect": (left_margin, y - 3, right_margin, y + entry_font_size),
                "target_page": target_page,
                "height": height,
            }
        )

        y -= line_height

    c.save()
    return pages_created, link_info


def estimate_toc_pages(toc_data: list[tuple[str, int]], page_size=A4) -> int:
    """
    Estimate how many pages the TOC will need.
    """
    if not toc_data:
        return 0

    _, height = page_size
    top_margin = height - 50
    bottom_margin = 60
    line_height = 20
    title_space = 35

    usable_height = top_margin - bottom_margin - title_space
    entries_per_page = int(usable_height / line_height)

    if entries_per_page <= 0:
        return len(toc_data)

    return (len(toc_data) + entries_per_page - 1) // entries_per_page


def flatten_outline_structure(
    outline_structure: list[dict],
    file_page_starts: dict[str, int],
) -> list[tuple[str, int, int]]:
    """
    Flatten hierarchical outline structure into a list for TOC rendering.

    Args:
        outline_structure: Hierarchical outline from parse_manifest_file
        file_page_starts: Dict mapping filename to starting page number (0-indexed)

    Returns:
        List of (title, page_number, level) tuples for TOC rendering.
    """
    flattened = []

    def process_item(item: dict):
        title = item.get("title")
        level = item.get("level", 1)
        file = item.get("file")
        children = item.get("children", [])

        # Determine page for this item
        page = None
        if file and file in file_page_starts:
            page = file_page_starts[file]
        elif children:
            # Link to first child's page
            for child in children:
                child_file = child.get("file")
                if child_file and child_file in file_page_starts:
                    page = file_page_starts[child_file]
                    break

        # Use title or cleaned filename
        display_title = (
            title if title else (clean_outline_title(file) if file else None)
        )

        if display_title and page is not None:
            flattened.append((display_title, page, level))

        # Process children recursively
        for child in children:
            process_item(child)

    for item in outline_structure:
        process_item(item)

    return flattened


def create_hierarchical_toc_pdf(
    toc_data: list[tuple[str, int, int]],
    output_path: str,
    toc_page_count: int,
    page_size=A4,
    cover_pages: int = 0,
) -> tuple[int, list[dict]]:
    """
    Create a PDF with hierarchical table of contents.

    Levels have different font sizes and indentation:
    - Level 1: 13pt font, no indent (section headers)
    - Level 2: 11pt font, 20px indent
    - Level 3: 10pt font, 40px indent
    - Level 4+: 9pt font, 60px indent

    Args:
        toc_data: List of (title, page_number, level) tuples
        output_path: Path for the TOC PDF
        toc_page_count: Number of TOC pages (for adjusting target page numbers)
        page_size: Page size (default A4)
        cover_pages: Number of cover pages that precede TOC in final PDF

    Returns:
        Tuple of (number of pages created, list of link info dicts)
    """
    font_name = _register_arial_font()

    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size

    # Margins and layout
    left_margin = 50
    right_margin = width - 50
    top_margin = height - 50
    bottom_margin = 60
    title_font_size = 16

    # Font sizes and indentation by level
    level_config = {
        1: {"font_size": 13, "indent": 0, "line_height": 24, "bold": True},
        2: {"font_size": 11, "indent": 20, "line_height": 20, "bold": False},
        3: {"font_size": 10, "indent": 40, "line_height": 18, "bold": False},
        4: {"font_size": 9, "indent": 60, "line_height": 16, "bold": False},
    }

    def get_level_config(level: int) -> dict:
        """Get config for a level, defaulting to level 4+ config for deep nesting."""
        if level in level_config:
            return level_config[level]
        # For deeper levels, increase indent but keep font size at 9
        return {
            "font_size": 9,
            "indent": 60 + (level - 4) * 15,
            "line_height": 16,
            "bold": False,
        }

    pages_created = 0
    link_info = []

    def start_new_page(is_first=False):
        nonlocal pages_created
        if not is_first:
            c.showPage()
        pages_created += 1

        # Draw title on each page
        if font_name == "Helvetica":
            c.setFont("Helvetica-Bold", title_font_size)
        else:
            c.setFont(font_name, title_font_size)
        c.drawString(left_margin, top_margin, "Table of Contents")

        return top_margin - 35

    y = start_new_page(is_first=True)

    for title, original_page_num, level in toc_data:
        config = get_level_config(level)
        font_size = config["font_size"]
        indent = config["indent"]
        line_height = config["line_height"]
        is_bold = config["bold"]

        if y < bottom_margin:
            y = start_new_page()

        # Target page in final PDF
        target_page = original_page_num + toc_page_count

        # Display page number (1-indexed)
        display_page = target_page + 1

        # Set font
        if is_bold and font_name == "Helvetica":
            c.setFont("Helvetica-Bold", font_size)
        elif is_bold:
            # For Arial, we use the same font (no bold variant registered)
            c.setFont(font_name, font_size)
        else:
            c.setFont(font_name, font_size)

        entry_left = left_margin + indent

        # Draw title in dark blue (darker for level 1)
        if level == 1:
            c.setFillColorRGB(0, 0, 0.7)
        else:
            c.setFillColorRGB(0.1, 0.1, 0.6)
        c.drawString(entry_left, y, title)

        # Draw page number (right-aligned) in black
        c.setFillColorRGB(0, 0, 0)
        c.drawRightString(right_margin, y, str(display_page))

        # Draw dotted line between title and page number
        title_width = c.stringWidth(title, font_name, font_size)
        page_width = c.stringWidth(str(display_page), font_name, font_size)
        dot_start = entry_left + title_width + 10
        dot_end = right_margin - page_width - 10

        if dot_end > dot_start:
            c.setFillColorRGB(0.5, 0.5, 0.5)
            dot_x = dot_start
            while dot_x < dot_end:
                c.drawString(dot_x, y, ".")
                dot_x += 5

        # Store link info
        link_info.append(
            {
                "toc_page": pages_created - 1,
                "rect": (left_margin, y - 3, right_margin, y + font_size),
                "target_page": target_page,
                "height": height,
            }
        )

        y -= line_height

    c.save()
    return pages_created, link_info


def estimate_hierarchical_toc_pages(
    toc_data: list[tuple[str, int, int]], page_size=A4
) -> int:
    """
    Estimate how many pages the hierarchical TOC will need.
    """
    if not toc_data:
        return 0

    _, height = page_size
    top_margin = height - 50
    bottom_margin = 60
    title_space = 35

    usable_height = top_margin - bottom_margin - title_space

    # Calculate total height needed based on level-specific line heights
    level_line_heights = {1: 24, 2: 20, 3: 18, 4: 16}
    total_height = 0
    for _, _, level in toc_data:
        line_height = level_line_heights.get(level, 16)
        total_height += line_height

    if usable_height <= 0:
        return len(toc_data)

    return max(1, (total_height + usable_height - 1) // usable_height)


def add_toc_to_pdf(
    file_path: Path,
    has_cover: bool = False,
    outline_structure: list[dict] | None = None,
    file_page_starts: dict[str, int] | None = None,
) -> None:
    """
    Add a clickable table of contents to a PDF.
    The TOC is based on the PDF's outline/bookmarks, or a hierarchical
    outline structure from a manifest file.

    Args:
        file_path: Path to the PDF file
        has_cover: If True, TOC is inserted after the first page (cover).
                   Cover page should not have an outline entry.
        outline_structure: Optional hierarchical outline from manifest parsing.
                          When provided, creates a hierarchical TOC with
                          different font sizes and indentation per level.
        file_page_starts: Dict mapping filename to page number (required
                         when outline_structure is provided).
    """
    try:
        # Determine if using hierarchical mode (manifest)
        use_hierarchical = (
            outline_structure is not None and file_page_starts is not None
        )

        if use_hierarchical:
            # Flatten the hierarchical structure for TOC rendering
            hierarchical_toc_data = flatten_outline_structure(
                outline_structure, file_page_starts
            )
            if not hierarchical_toc_data:
                click.echo("No TOC entries found in outline structure.")
                return
        else:
            # Get outline data from the PDF (cover is already excluded from outline)
            toc_data = get_outline_data(file_path)

            if not toc_data:
                click.echo("PDF has no outline. Use -o flag to add outline first.")
                return

        # Number of cover pages (inserted before TOC)
        cover_pages = 1 if has_cover else 0

        # Create TOC PDF in temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            toc_pdf_path = tmp.name

        if use_hierarchical:
            # Estimate TOC pages needed for hierarchical
            estimated_pages = estimate_hierarchical_toc_pages(hierarchical_toc_data)

            # Create hierarchical TOC
            actual_toc_pages, link_info = create_hierarchical_toc_pdf(
                hierarchical_toc_data,
                toc_pdf_path,
                estimated_pages,
                cover_pages=cover_pages,
            )

            # If estimate was wrong, recreate with correct page count
            if actual_toc_pages != estimated_pages:
                actual_toc_pages, link_info = create_hierarchical_toc_pdf(
                    hierarchical_toc_data,
                    toc_pdf_path,
                    actual_toc_pages,
                    cover_pages=cover_pages,
                )
        else:
            # Estimate TOC pages needed
            estimated_pages = estimate_toc_pages(toc_data)

            # Create TOC (visual content + link positions)
            actual_toc_pages, link_info = create_toc_pdf(
                toc_data, toc_pdf_path, estimated_pages, cover_pages=cover_pages
            )

            # If estimate was wrong, recreate with correct page count
            if actual_toc_pages != estimated_pages:
                actual_toc_pages, link_info = create_toc_pdf(
                    toc_data, toc_pdf_path, actual_toc_pages, cover_pages=cover_pages
                )

        # Merge: Cover (if any) + TOC + rest of original PDF
        writer = pypdf.PdfWriter()
        original_reader = pypdf.PdfReader(file_path)

        # Add cover page(s) first if present
        for i in range(cover_pages):
            if i < len(original_reader.pages):
                writer.add_page(original_reader.pages[i])

        # Add TOC pages
        toc_reader = pypdf.PdfReader(toc_pdf_path)
        toc_start_idx = cover_pages  # Where TOC pages start in final PDF
        for page in toc_reader.pages:
            writer.add_page(page)

        # Add remaining original PDF pages (after cover)
        for i in range(cover_pages, len(original_reader.pages)):
            writer.add_page(original_reader.pages[i])

        # Add clickable links to TOC pages
        for info in link_info:
            toc_page_idx = toc_start_idx + info["toc_page"]
            target_page_idx = info["target_page"]
            rect = info["rect"]

            x1, y1, x2, y2 = rect

            # Create link annotation
            link_annotation = DictionaryObject()
            link_annotation.update(
                {
                    NameObject("/Type"): NameObject("/Annot"),
                    NameObject("/Subtype"): NameObject("/Link"),
                    NameObject("/Rect"): ArrayObject(
                        [
                            FloatObject(x1),
                            FloatObject(y1),
                            FloatObject(x2),
                            FloatObject(y2),
                        ]
                    ),
                    NameObject("/Border"): ArrayObject(
                        [
                            NumberObject(0),
                            NumberObject(0),
                            NumberObject(0),
                        ]
                    ),
                    NameObject("/Dest"): ArrayObject(
                        [
                            writer.pages[target_page_idx].indirect_reference,
                            NameObject("/Fit"),
                        ]
                    ),
                }
            )

            # Add annotation to the TOC page
            page = writer.pages[toc_page_idx]
            if "/Annots" not in page:
                page[NameObject("/Annots")] = ArrayObject()
            page["/Annots"].append(link_annotation)

        # Rebuild outline with adjusted page numbers
        writer.outline.clear()

        if use_hierarchical:
            # Rebuild hierarchical outline
            def add_outline_items(items: list[dict], parent=None):
                for item in items:
                    title = item.get("title")
                    file = item.get("file")
                    children = item.get("children", [])

                    # Get page number
                    page_num = None
                    if file and file in file_page_starts:
                        page_num = file_page_starts[file] + actual_toc_pages
                    elif children:
                        # Link to first child
                        for child in children:
                            child_file = child.get("file")
                            if child_file and child_file in file_page_starts:
                                page_num = (
                                    file_page_starts[child_file] + actual_toc_pages
                                )
                                break

                    display_title = (
                        title
                        if title
                        else (clean_outline_title(file) if file else None)
                    )

                    if display_title and page_num is not None:
                        outline_item = writer.add_outline_item(
                            display_title, page_num, parent=parent
                        )
                        # Add children recursively
                        if children:
                            add_outline_items(children, parent=outline_item)

            add_outline_items(outline_structure)
        else:
            # Cover page has no outline entry, so all entries need TOC offset
            for title, original_page_num in toc_data:
                new_page_num = original_page_num + actual_toc_pages
                writer.add_outline_item(title, new_page_num)

        # Write the final PDF
        with open(file_path, "wb") as f:
            writer.write(f)

        # Cleanup temp file
        try:
            os.remove(toc_pdf_path)
        except Exception:
            pass

        if has_cover:
            click.echo(
                f"Added {actual_toc_pages} TOC page(s) after cover to {file_path.name}"
            )
        else:
            click.echo(f"Added {actual_toc_pages} TOC page(s) to {file_path.name}")

    except Exception as e:
        click.echo(f"Error adding TOC: {e}")


if __name__ == "__main__":
    pass
