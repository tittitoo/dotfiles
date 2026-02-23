#!/usr/bin/env -S uv run --quiet --no-upgrade --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "click",
# "xlwings",
# "python-decouple",
# "pandas",
# "pypdf",
# "docx2pdf",
# "reportlab",
# "openpyxl",
# "playwright",
# ]
# ///

# For the import, remember to put it in the script above. Script is read during runtime.
# Heavy imports (docx2pdf, xlwings, pypdf, etc.) are lazy-loaded in commands that need them
import logging
import os
import platform
import re
import shutil
import subprocess
import getpass
from datetime import datetime
from pathlib import Path

import click

# Version
# Recommended is to define in __init__.py but I am doing it here.
__version__ = "0.1.0"

# Handle case for different users
username = getpass.getuser()
match username:
    case "oliver":
        RFQ = "~/OneDrive - Jason Electronics Pte Ltd/Shared Documents/@rfqs/"
        HO = "~/OneDrive - Jason Electronics Pte Ltd/Shared Documents/@handover/"
        CO = "~/OneDrive - Jason Electronics Pte Ltd/Shared Documents/@costing/"
        DOCS = "~/OneDrive - Jason Electronics Pte Ltd/Shared Documents/@docs/"
        TOOLS = "~/OneDrive - Jason Electronics Pte Ltd/Shared Documents/@tools/"
        BID_ALIAS = f"alias bid=\"uv run --quiet '{Path(r'~/OneDrive - Jason Electronics Pte Ltd/Shared Documents/@tools/bid.py').expanduser().resolve()}'\""

    case "carol_lim":
        RFQ = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@rfqs/"
        DOCS = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@docs/"
        TOOLS = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@tools/"
        BID_ALIAS = f"alias bid=\"uv run --quiet '{Path(r'~/Jason Electronics Pte Ltd/Bid Proposal - @tools/bid.py').expanduser().resolve()}'\""

    case _:
        RFQ = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@rfqs/"
        HO = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@handover/"
        CO = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@costing/"
        DOCS = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@docs/"
        TOOLS = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@tools/"
        BID_ALIAS = f"alias bid=\"uv run --quiet '{Path(r'~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@tools/bid.py').expanduser().resolve()}'\""


RESTRICTED_FOLDER = [
    "@rfqs",
    "@costing",
    "@handover",
    "@tools",
    "@commercial-review",
    "@projects",
    "Documents",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command()
@click.option("-y", "--yes", is_flag=True, help="Answer yes to the current directory")
def word2pdf(yes: bool):
    """
    (Batch) Convert word file to pdf in given directory.
    Require MS Word to be installed as it is doing the conversion.
    """
    import docx2pdf

    directory = Path.cwd()
    if not yes:
        click.confirm(
            f"The command will convert all the word files (only .docx (case sensitive)) in '{directory}'",
            abort=True,
        )
    docx2pdf.convert(directory)


def normalize_job_code(search_term: str) -> str:
    """Normalize job code input.

    If only 3 digits are given, prepend 'J12' to make a full job code.
    E.g., '786' becomes 'J12786'
    """
    search_term = search_term.strip()
    if search_term.isdigit() and len(search_term) == 3:
        return f"J12{search_term}"
    return search_term


def find_project_folder(search_term: str) -> list[tuple[Path, int]]:
    """Search for project folders matching the search term.

    Searches in @rfqs/<year>/ for years from current year down to 2023.
    Returns list of (folder_path, year) tuples for folders starting with search_term.
    """
    search_term = normalize_job_code(search_term)
    rfqs_path = Path(RFQ).expanduser()

    if not rfqs_path.exists():
        return []

    matches = []
    current_year = datetime.now().year

    for year in range(current_year, 2022, -1):  # Down to 2023
        year_path = rfqs_path / str(year)
        if not year_path.exists():
            continue

        for folder in year_path.iterdir():
            if folder.is_dir() and folder.name.upper().startswith(search_term.upper()):
                matches.append((folder, year))

    return matches


def get_next_vo_number(vo_folder: Path) -> int:
    """Get the next available VO number.

    Scans existing NN-VO folders and returns the next available number.
    """
    if not vo_folder.exists():
        return 1

    existing_numbers = []
    for folder in vo_folder.iterdir():
        if folder.is_dir():
            # Match pattern like "01-VO", "02-VO", etc.
            match = re.match(r"^(\d{2})-VO\b", folder.name)
            if match:
                existing_numbers.append(int(match.group(1)))

    if not existing_numbers:
        return 1

    return max(existing_numbers) + 1


def create_vo_structure(vo_path: Path) -> None:
    """Create the VO subfolder structure."""
    iso_date = datetime.now().strftime("%Y-%m-%d")

    folders = [
        vo_path / "00-ITB" / iso_date,
        vo_path / "01-Commercial" / "00-Arc",
        vo_path / "02-Technical" / "00-Arc",
        vo_path / "03-Supplier" / "00-Arc",
        vo_path / "04-Datasheet" / "00-Arc",
        vo_path / "05-PO" / "00-Arc",
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)


def get_handover_candidates(project_path: Path) -> list[tuple[str, Path]]:
    """Get list of handover candidates for a project.

    Returns list of (display_name, source_path) tuples:
    - Main project folder as "00-MAIN"
    - Any NN-VO folders from 07-VO/
    """
    candidates = [("00-MAIN", project_path)]

    vo_parent = project_path / "07-VO"
    if vo_parent.exists():
        vo_folders = sorted(
            [
                f
                for f in vo_parent.iterdir()
                if f.is_dir() and re.match(r"^\d{2}-VO\b", f.name)
            ],
            key=lambda x: x.name,
        )
        for vo_folder in vo_folders:
            candidates.append((vo_folder.name, vo_folder))

    return candidates


def is_folder_not_empty(path: Path) -> bool:
    """Check if folder exists and is not empty."""
    if not path.exists():
        return False
    return any(path.iterdir())


def is_conforming_handover_folder(folder: Path) -> bool:
    """Check if folder was created by bid ho (has expected structure).

    Returns True if folder doesn't exist (new folder will conform) or
    if it has at least 3 of the expected subfolders.
    """
    if not folder.exists():
        return True  # New folder, will conform

    expected = {
        "00-ITB",
        "01-PO",
        "02-Technical",
        "03-Supplier",
        "04-Datasheet",
        "05-Cost",
    }
    existing = {f.name for f in folder.iterdir() if f.is_dir()}

    # Check if it has at least 3 expected folders
    return len(expected & existing) >= 3


def sync_folder(source: Path, dest: Path) -> bool:
    """One-way mirror sync from source to dest.

    Returns True if sync was performed, False if source was empty/missing.
    Mirrors source to dest: adds new files, updates changed files, deletes
    files in dest that don't exist in source. Empty folders are skipped.
    """
    if not is_folder_not_empty(source):
        return False

    dest.mkdir(parents=True, exist_ok=True)

    # Get only files (not directories) - empty folders like 00-Arc are skipped
    source_files = {p.relative_to(source) for p in source.rglob("*") if p.is_file()}
    dest_files = {p.relative_to(dest) for p in dest.rglob("*") if p.is_file()}

    # Delete files in dest that don't exist in source (purge)
    for rel_path in dest_files - source_files:
        dest_path = dest / rel_path
        if dest_path.exists():
            dest_path.unlink()

    # Clean up empty directories in dest
    for dir_path in sorted(dest.rglob("*"), reverse=True):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            dir_path.rmdir()

    # Copy/update files from source to dest
    for rel_path in source_files:
        source_path = source / rel_path
        dest_path = dest / rel_path

        # Copy if dest doesn't exist or source is newer
        if (
            not dest_path.exists()
            or source_path.stat().st_mtime > dest_path.stat().st_mtime
        ):
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)

    return True


def perform_handover_sync(source_root: Path, dest_root: Path, is_vo: bool) -> None:
    """Perform the handover sync operations.

    Args:
        source_root: Source folder (project root or VO folder)
        dest_root: Destination folder in @handover
        is_vo: True if this is a VO handover (affects PO folder mapping)
    """
    dest_root.mkdir(parents=True, exist_ok=True)

    # Define sync mappings: (source_name, dest_name)
    # PO folder differs: main project has 06-PO, VO has 05-PO
    po_source = "05-PO" if is_vo else "06-PO"

    sync_mappings = [
        ("00-ITB", "00-ITB"),
        (po_source, "01-PO"),
        ("02-Technical", "02-Technical"),
        ("03-Supplier", "03-Supplier"),
        ("04-Datasheet", "04-Datasheet"),
        ("05-Drawing", "06-Drawing"),
    ]

    for source_name, dest_name in sync_mappings:
        source_path = source_root / source_name
        dest_path = dest_root / dest_name

        if sync_folder(source_path, dest_path):
            click.echo(f"  Synced: {source_name} -> {dest_name}")
        else:
            click.echo(f"  Skipped: {source_name} (empty or missing)")

    # Always create 05-Cost folder
    cost_folder = dest_root / "05-Cost"
    cost_folder.mkdir(parents=True, exist_ok=True)
    click.echo("  Created: 05-Cost")


def open_with_default_app(file_path: Path):
    "Open file_path with default application"
    if platform.system() == "Windows":
        try:
            subprocess.run(["explorer", file_path.expanduser().resolve()])
        except Exception as _:
            click.echo("Not yet implemented.")
    elif platform.system() == "Darwin":
        click.launch("file://" + str(file_path.expanduser().resolve()))
    else:
        click.echo("Not implemented for this platform")


def remove_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            click.echo(f"Deleted: {folder_path}")
            return True
        except OSError as e:
            click.echo(f"Error deleting folder: {e}")
            return False
    else:
        click.echo(f"Folder {folder_path} does not exist.")


def require_rename(file_name: str, flag: bool = False) -> tuple[str, bool]:
    """
    Check if file meets required naming specs
    If not, suggest renaming and the name

    Specs:
    Strip file name of white space at the end
    Put file extension in lowercase
    `word-` to `word -`
    One or more '-' to single '-'
    One or more '_' to single '_'
    One or more ` . ` to single ` `
    ` _word` to ` word`
    One or more `#`, `_` followed by space to single space
    Delete `[` or `]`
    Remove RE, SV, FW, FWD, EXTERNAL, URGENT, 回复 at the start of email, case insensitive
    No double 'space' or more

    """

    file, extension = os.path.splitext(file_name)
    new_file_name = file.strip() + extension.lower()

    new_file_name = re.sub(r"(\b\w+\b)-\s", r"\1 - ", new_file_name)
    # new_file_name = re.sub(r"-{1,}", " ", new_file_name)
    new_file_name = re.sub(r"-{2,}", "-", new_file_name)
    new_file_name = re.sub(r"_{2,}", "_", new_file_name)
    new_file_name = re.sub(r" \.+ ", " ", new_file_name)
    new_file_name = re.sub(r" _(\w+)", r" \1", new_file_name)
    new_file_name = re.sub(r"(#+|_+\s{1,})", r" ", new_file_name)
    new_file_name = re.sub(r"(\[+)", "", new_file_name)
    new_file_name = re.sub(r"(\]+)", "", new_file_name)
    new_file_name = re.sub(r"^(RE(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(SV(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(AW(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(FW(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(FWD(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(
        r"^(回复(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE
    )
    new_file_name = re.sub(
        r"^(URGENT(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE
    )
    new_file_name = re.sub(
        r"^(EXTERNAL(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE
    )
    new_file_name = re.sub(
        r"^(EXTERNALRE(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE
    )
    new_file_name = re.sub(r"^(FWD(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(FW(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(SV(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(RE(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    # new_file_name = re.sub(
    #     r"(-+|\s{1,})", " ", new_file_name, flags=re.IGNORECASE
    # )  # remove hyphen
    new_file_name = re.sub(r"\s{2,}", " ", new_file_name)
    if new_file_name != file_name:
        flag = True
        return (new_file_name, flag)
    return (file_name, flag)


def rename_file(old_file_name: Path, new_file_name: Path) -> bool:
    "Rename old_file_name to new_file_name"
    try:
        if os.path.exists(new_file_name):
            # Handle case where file with same extension but different case exists
            if new_file_name.suffix != old_file_name.suffix:
                os.rename(old_file_name, new_file_name)
                return True
            # Othereise skip
            click.echo(f"File with the same name as '{new_file_name}' already exists.")
            return False
        os.rename(old_file_name, new_file_name)
        return True
    except OSError as e:
        click.echo(f"Error renaming file: '{old_file_name}' caused by {e}")
        return False


# Create project folder structure
@click.command()
@click.argument("folder_name", default="")
def init(folder_name: str) -> None:
    """
    Create folder structure for project in @rfqs.
    Search for the latest year, create one if it does not exists.
    Then create the required folder structure in it.
    """
    from util import excelx

    # Handle case where @rfqs does not exists
    if not Path(RFQ).expanduser().exists():
        click.echo("The folder @rfqs does not exist. Check if you have access.")
        return

    if folder_name == "":
        folder_name = click.prompt("Please enter folder name to create")
    # Normalize dashes: convert en-dash (–) and em-dash (—) to hyphen-minus (-)
    folder_name = folder_name.replace("–", "-").replace("—", "-")
    current_year = datetime.now().year
    path = Path(RFQ).expanduser()
    folders = []
    for item in path.iterdir():
        if item.is_dir():
            folders.append(item.name)
    if str(current_year) in folders:
        new_path = path / Path(str(current_year))
    else:
        new_path = path / Path(str(current_year))
        new_path.mkdir(exist_ok=True)
    # Create subdirectories if the folder_name not exists
    new_path = new_path / folder_name
    if new_path.exists():
        click.echo("The folder already exists.")
        # Create new commercial Proposal
        if click.confirm(
            "Do you want to create a new Commercial Proposal?", default=True
        ):
            version = click.prompt(
                "Version No, default:", default="B0", show_default=True
            )
            version = str(version).upper()
            template_folder = (
                Path(RFQ).expanduser().parent.absolute().resolve() / "@tools/resources"
            )
            template = "Template.xlsx"
            commercial_folder = new_path / "01-Commercial"
            commercial_file = folder_name + " " + str(version) + ".xlsx"
            jobcode = folder_name.split()[0]
            excelx.create_excel_from_template(
                template_folder,
                template,
                commercial_folder,
                commercial_file,
                jobcode,
                version,
            )
        if click.confirm("Do you want to open the project folder?", abort=True):
            open_with_default_app(new_path)
            return
    else:
        if click.confirm(
            f"'{new_path}' will be created. Continue?", default=True, abort=True
        ):
            new_path.mkdir()
            iso_date = datetime.now().strftime("%Y-%m-%d")
            itb_specs = new_path / "00-ITB" / iso_date
            itb_specs.mkdir(parents=True, exist_ok=True)
            commercial = new_path / "01-Commercial/00-Arc"
            commercial.mkdir(parents=True, exist_ok=True)
            technical = new_path / "02-Technical/00-Arc"
            technical.mkdir(parents=True, exist_ok=True)
            supplier = new_path / "03-Supplier/00-Arc"
            supplier.mkdir(parents=True, exist_ok=True)
            datasheet = new_path / "04-Datasheet/00-Arc"
            datasheet.mkdir(parents=True, exist_ok=True)
            drawing = new_path / "05-Drawing/00-Arc"
            drawing.mkdir(parents=True, exist_ok=True)
            po = new_path / "06-PO/00-Arc"
            po.mkdir(parents=True, exist_ok=True)
            vo = new_path / "07-VO"
            vo.mkdir(parents=True, exist_ok=True)
            toolkit = new_path / "08-Toolkit"
            toolkit.mkdir(parents=True, exist_ok=True)
            click.echo(f"Created fodler {new_path}")
            # Create new commercial Proposal
            if click.confirm(
                "Do you want to create a new Commercial Proposal?", default=True
            ):
                version = click.prompt(
                    "Version No, default:", default="B0", show_default=True
                )
                version = str(version).upper()
                template_folder = (
                    Path(RFQ).expanduser().parent.absolute().resolve()
                    / "@tools/resources"
                )
                template = "Template.xlsx"
                commercial_folder = new_path / "01-Commercial"
                commercial_file = folder_name + " " + str(version) + ".xlsx"
                jobcode = folder_name.split()[0]
                excelx.create_excel_from_template(
                    template_folder,
                    template,
                    commercial_folder,
                    commercial_file,
                    jobcode,
                    version,
                )
            # Ask for the folder to be opened
            if click.confirm(
                "Do you want to open the project folder?",
                abort=True,
            ):
                open_with_default_app(new_path)
        else:
            click.echo("Folder creation aborted.")


@click.command()
@click.argument("folder_name", default="")
@click.option("-d", "--dry-run", is_flag=True, help="Dry run mode")
@click.option("-y", "--yes", is_flag=True, help="Answer yes to the current directory")
@click.option(
    "-r",
    "--remove-git",
    is_flag=True,
    help="Delete .git folder and .gitignore if exists",
)
def clean(folder_name: str, dry_run: bool, remove_git: bool, yes: bool) -> None:
    """
    Clean file names in folder. Default search path is @rfqs.
    If folder is given, clean the folder.
    If not, search the folder in @rfqs and clean.
    """
    if folder_name == "":
        if yes:
            folder_name = Path.cwd().name
        else:
            folder_name = click.prompt(
                (
                    "Please enter folder name to clean. "
                    "Default search path is in @rfqs. \n"
                    "Press `Enter` to choose current folder:"
                ),
                default=Path.cwd().name,
                type=str,
            )
    if (
        folder_name in RESTRICTED_FOLDER
        or folder_name.isdigit()  # Main folder in @rfqs
        or folder_name == Path.home().name
    ):
        click.echo(
            f"You are not allowed to clean '{folder_name}' directly. "
            "Please choose a subfolder."
        )
        return
    if folder_name == Path.cwd().name:
        clean_folder(Path.cwd(), dry_run=dry_run, yes=yes)
    else:
        clean_rfqs(folder_name, remove_git=remove_git, dry_run=dry_run)


def clean_folder(start_path, dry_run=False, yes=False):
    "Clean folder"
    rename_list = []
    for root, _, files in os.walk(start_path):
        for file in files:
            check = require_rename((file))
            if check[1]:
                rename_list.append((root, file, check[0]))
    if not dry_run:
        if not rename_list:
            click.echo("No file required to be renamed. Folder clean 😎")
            return
        click.echo("Here is the list of files to rename.")
        for item in rename_list:
            click.echo(f"{item[1]} -> {item[2]}")
        click.echo(f"{len(rename_list)} files to rename")
        if not yes:
            click.confirm("Do you want to rename the files?", abort=True)
        click.echo("Renaming files")
        count = 0
        for item in rename_list:
            check = rename_file(
                Path(item[0]).joinpath(item[1]), Path(item[0]).joinpath(item[2])
            )
            if check:
                count += 1
                click.echo(f"Renamed: '{item[1]}' -> '{item[2]}'")
            else:
                # Handle the case where file with same name exists
                # Append -000, try once
                new_file_name = Path(item[2]).stem + "-000" + Path(item[2]).suffix
                check_again = rename_file(
                    Path(item[0]).joinpath(item[1]),
                    Path(item[0]).joinpath(new_file_name),
                )
                if check_again:
                    count += 1
                    click.echo(
                        (
                            f"Since the same file name exists '{item[1]}' "
                            f"renamed to '{new_file_name}' instead appending '-000'"
                        )
                    )
                else:
                    click.echo(f"Failed to rename '{item[1]}'")
        click.echo(f"Total {count} files renamed.")
        return
    else:  # if dry_run
        if not rename_list:
            click.echo("No file required to be renamed. Folder clean 😎")
            return
        click.echo("Here is the list of files to rename.")
        for item in rename_list:
            click.echo(f"'{item[1]}' -> '{item[2]}'")
        click.echo(f"{len(rename_list)} files to rename")


def clean_rfqs(folder_name, remove_git=False, dry_run=False):
    "Search for folder name in @rfqs and clean it"
    # Handle case where @rfqs does not exists
    if not Path(RFQ).expanduser().exists():
        click.echo("The folder @rfqs does not exist. Check if you have access.")
        return
    rfqs = Path(RFQ).expanduser()
    folders = []
    for _, dirs, _ in os.walk(rfqs):
        for dir in dirs:
            folders.append(dir)
        dirs.clear()  # To stop at top level folder
        folders = [str(item) for item in folders if str(item).isdigit()]
        folders = sorted(folders, key=lambda x: int(x), reverse=True)

    # Walk files in the second level
    # rename_list = []
    for level in folders:
        for _, dirs, files in os.walk(rfqs / level):
            for dir in dirs:
                if folder_name == dir:
                    start_path = Path(rfqs / level / dir)
                    # Check for .git folder and .gitignore
                    for _, dirs, files in os.walk(start_path):
                        if ".git" in dirs:
                            git_path = Path(rfqs / level / dir / ".git")
                            click.echo(f"Found {git_path}")
                            if remove_git:
                                remove_folder(git_path)
                        if ".gitignore" in files:
                            gitignore_path = Path(rfqs / level / dir / ".gitignore")
                            click.echo(f"Found {gitignore_path}")
                            if remove_git:
                                try:
                                    os.remove(gitignore_path)
                                    click.echo(f"Deleted: {gitignore_path}")
                                except OSError as e:
                                    click.echo(f"Error deleting file: {e}")
                        dirs.clear()  # Stop at top level folder
                    # Now clean folder
                    clean_folder(start_path, dry_run=dry_run)
                    return
            dirs.clear()  # Stop at top level folder
    click.echo(f"{folder_name} cannot be found in {rfqs}")


@click.command()
def setup():
    """
    Setup necessary environment variables and alias.
    """
    if platform.system() == "Linux":
        pass
    elif platform.system() == "Windows":
        # Step 1 — Create .managed_python folder
        managed_python = Path.home() / ".managed_python"
        managed_python.mkdir(exist_ok=True)
        click.echo(f"Created {managed_python}")

        # Step 2 — Copy pyproject.toml from @tools
        tools_path = Path(TOOLS).expanduser()
        shutil.copy2(tools_path / "pyproject.toml", managed_python / "pyproject.toml")
        click.echo("Copied pyproject.toml to .managed_python.")

        # Step 3 — Run uv sync
        click.echo("Running uv sync...")
        subprocess.run(["uv", "sync"], cwd=str(managed_python), check=True)
        click.echo("uv sync complete.")

        # Step 4 — Add .venv/Scripts Python to user PATH (top priority)
        python_path = str(managed_python / ".venv" / "Scripts")
        result = subprocess.run(
            [
                "powershell",
                "-c",
                "[Environment]::GetEnvironmentVariable('Path', 'User')",
            ],
            capture_output=True,
            text=True,
        )
        current_path = result.stdout.strip()
        if python_path.lower() not in current_path.lower():
            new_path = python_path + ";" + current_path
            subprocess.run(
                [
                    "powershell",
                    "-c",
                    f"[Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')",
                ],
                check=True,
            )
            click.echo(f"Added {python_path} to user PATH.")
        else:
            click.echo(f"{python_path} is already in user PATH, skipping.")

        # Check if Excel is running before steps 5 & 6 (both require Excel closed)
        excel_closed = True
        result = subprocess.run(
            ["powershell", "-c", "Get-Process excel -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            if click.confirm("Excel is running. Close it to continue setup?"):
                subprocess.run(["powershell", "-c", "Stop-Process -Name excel -Force"])
            else:
                click.echo("Skipping xlwings add-in install and PERSONAL.XLSB copy.")
                excel_closed = False

        if excel_closed:
            # Step 5 — Install xlwings add-in
            click.echo("Installing xlwings add-in...")
            subprocess.run(
                ["xlwings", "addin", "install"],
                cwd=str(managed_python),
                check=True,
            )
            click.echo("xlwings add-in installed.")

            # Step 6 — Copy PERSONAL.XLSB to XLSTART
            personal_xlsb_src = tools_path / "PERSONAL.XLSB"
            xlstart = (
                Path.home() / "AppData" / "Roaming" / "Microsoft" / "Excel" / "XLSTART"
            )
            personal_xlsb_dst = xlstart / "PERSONAL.XLSB"
            xlstart.mkdir(parents=True, exist_ok=True)
            shutil.copy2(personal_xlsb_src, personal_xlsb_dst)
            click.echo(f"Copied PERSONAL.XLSB to {xlstart}")

        # Step 7 — Ensure PERSONAL.XLSB opens hidden when Excel starts
        # This is controlled by VBA in PERSONAL.XLSB's ThisWorkbook module:
        #   Private Sub Workbook_Open()
        #       Windows(ThisWorkbook.Name).Visible = False
        #   End Sub
        # No action needed here — the file in @tools is pre-configured.

        # Step 8 — Make .managed_python folder hidden in Windows
        subprocess.run(
            ["attrib", "+H", str(managed_python)],
            check=True,
        )
        click.echo(f"Set {managed_python} as hidden.")

        # Step 9 — Set xlwings interpreter path to .managed_python/.venv python
        xlwings_conf_dir = Path.home() / ".xlwings"
        xlwings_conf_dir.mkdir(exist_ok=True)
        xlwings_conf = xlwings_conf_dir / "xlwings.conf"
        interpreter_path = str(managed_python / ".venv" / "Scripts" / "python.exe")
        pythonpath = str(tools_path).replace("@", "\\@")

        # Step 10 — Set xlwings PYTHONPATH to @tools folder and disable ADD_WORKBOOK_TO_PYTHONPATH
        # xlwings.conf uses CSV format: "KEY","VALUE"
        # Must use newline="" on both read and write to prevent \r\n → \r\r\n
        # double conversion, which causes VBA "Input past end of file" error 62
        import csv

        conf_lines = {}
        if xlwings_conf.exists():
            with open(xlwings_conf, newline="") as f:
                for row in csv.reader(f):
                    if len(row) >= 2:
                        conf_lines[row[0]] = row[1]
        conf_lines["INTERPRETER_WIN"] = interpreter_path
        conf_lines["PYTHONPATH"] = pythonpath
        conf_lines["ADD_WORKBOOK_TO_PYTHONPATH"] = "False"
        with open(xlwings_conf, "w", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            for k, v in conf_lines.items():
                writer.writerow([k, v])
        click.echo(f"Set xlwings interpreter to {interpreter_path}")
        click.echo(f"Set xlwings PYTHONPATH to {pythonpath}")
        click.echo("Disabled ADD_WORKBOOK_TO_PYTHONPATH.")

        # Step 11 — Copy Excel.officeUI ribbon customization
        # Replace hardcoded XLSTART path in onAction attributes with current user's
        # path (onAction needs the full path for application-level ribbon callbacks)
        office_ui_src = tools_path / "resources" / "Excel.officeUI"
        office_ui_dst = (
            Path.home()
            / "AppData"
            / "Local"
            / "Microsoft"
            / "Office"
            / "Excel.officeUI"
        )
        office_ui_dst.parent.mkdir(parents=True, exist_ok=True)
        content = office_ui_src.read_text(encoding="utf-8")
        user_xlstart = str(
            Path.home() / "AppData" / "Roaming" / "Microsoft" / "Excel" / "XLSTART"
        )
        xlstart_personal = f'{user_xlstart}\\PERSONAL.XLSB'
        content = re.sub(
            r'onAction="[^"]*\\PERSONAL\.XLSB!',
            lambda _: f'onAction="{xlstart_personal}!',
            content,
        )
        office_ui_dst.write_text(content, encoding="utf-8")
        click.echo(f"Copied Excel.officeUI to {office_ui_dst.parent}")

        # Git Bash setup — write .bashrc alias and .minttyrc font config
        with open(Path.home() / ".bashrc", "w") as f:
            f.write(f"{BID_ALIAS} \n")
        with open(Path.home() / ".minttyrc", "w") as f:
            f.write("FontFamily=Victor Mono\nFontSize=15\n")
        click.echo("Git Bash .bashrc and .minttyrc configured.")
    elif platform.system() == "Darwin":
        # click.echo(RFQ)
        # click.echo(BID_ALIAS)
        # bid_alias = f"alias bid=\"uv run --quiet {Path(r'~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@tools/bid.py').expanduser().resolve()}\""
        # click.echo(bid_alias)
        # click.echo(Path.home() / ".bash_profile")
        # click.echo(Path.home() / ".bashrc")
        pass
    else:
        pass


@click.command()
def test():
    test = Path("~/Downloads")
    open_with_default_app(test)


@click.command()
@click.argument("xl_file", default="")
@click.option(
    "-f",
    "--font",
    is_flag=True,
    help="Apply font formatting only (shows template menu, default: Arial Size 12)",
)
def beautify(xl_file: str, font: bool) -> None:
    """
    Beautify excel file.

    By default, applies smart width (based on content, max 80 chars, word wrap).
    Use -f to apply font formatting only (no smart width).
    """
    from util.beautify import beautify as _beautify

    ctx = click.Context(_beautify)
    ctx.invoke(_beautify, xl_file=xl_file, font=font)


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
    Combine PDFs in current folder (Alias: cpdf).

    If the combined file already exists, it will remove it first and re-combine.

    With --manifest flag, also searches for PDFs in the @docs SharePoint folder.
    """
    from util.pdfx import combine_pdf as _combine_pdf

    # Use DOCS as fallback directory when in manifest mode
    docs_path = DOCS if use_manifest else None

    ctx = click.Context(_combine_pdf)
    ctx.invoke(
        _combine_pdf,
        outline=outline,
        toc=toc,
        yes=yes,
        use_manifest=use_manifest,
        docs_path=docs_path,
    )


@click.command()
@click.argument("directory", default="", type=click.Path())
@click.option(
    "-i",
    "--import-file",
    "import_file",
    type=click.Path(exists=True),
    help="Import from SharePoint exported CSV/Excel file",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(),
    help="Export report to CSV file",
)
@click.option(
    "--api",
    is_flag=True,
    help="Use m365 CLI API (requires setup and admin consent)",
)
@click.option(
    "-f",
    "--fetch",
    "fetch_url",
    type=str,
    help="Fetch from SharePoint URL using browser automation",
)
@click.option(
    "-l",
    "--library",
    default="Documents",
    help="SharePoint library title for --fetch (default: Documents)",
)
@click.option(
    "--folder",
    default="",
    help="Folder path within library for --fetch (e.g., '@docs')",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Debug mode: show browser window for --fetch",
)
@click.option(
    "--month",
    "filter_month",
    type=str,
    default=None,
    help="Filter by month: YYYY-MM or range YYYY-MM:YYYY-MM. Default: current month",
)
@click.option(
    "--all-time",
    "all_time",
    is_flag=True,
    help="Show all data without time filtering",
)
@click.option(
    "--person",
    "filter_person",
    type=str,
    default=None,
    help="Filter to specific person. Use 'all' for everyone",
)
def audit(
    directory: str,
    import_file: str | None,
    output_file: str | None,
    api: bool,
    fetch_url: str | None,
    library: str,
    folder: str,
    debug: bool,
    filter_month: str | None,
    all_time: bool,
    filter_person: str | None,
):
    """
    Audit folder to track file contributions.

    \b
    Default audits @docs folder. For full author info, use --fetch or --import-file.

    \b
    Examples:
      bid audit -f URL --folder "@docs"                    # Current month, interactive person
      bid audit -f URL --folder "@docs" --person all       # Current month, all people
      bid audit -f URL --folder "@docs" --all-time         # All time, interactive person
      bid audit -f URL --folder "@docs" --month 2025-12    # Specific month
    """
    from util.audit import audit as _audit

    ctx = click.Context(_audit)
    ctx.invoke(
        _audit,
        directory=directory,
        import_file=import_file,
        output_file=output_file,
        api=api,
        fetch_url=fetch_url,
        library=library,
        folder=folder,
        debug=debug,
        filter_month=filter_month,
        all_time=all_time,
        filter_person=filter_person,
    )


@click.command()
@click.argument("folder_name", default="")
def vo(folder_name: str) -> None:
    """
    Create VO (Variation Order) folder structure under an existing project.

    Searches for the project folder in @rfqs and creates a new VO subfolder
    with the standard folder structure.
    """
    # Handle case where @rfqs does not exist
    if not Path(RFQ).expanduser().exists():
        click.echo("The folder @rfqs does not exist. Check if you have access.")
        return

    # Get project folder name/job code
    if folder_name == "":
        folder_name = click.prompt("Please enter project folder name or job code")

    # Search for matching folders
    matches = find_project_folder(folder_name)

    if not matches:
        click.echo(f"No project folder found matching '{folder_name}'")
        return

    # Handle multiple matches
    if len(matches) == 1:
        project_path, year = matches[0]
    else:
        click.echo("Multiple folders found:")
        for i, (path, year) in enumerate(matches, 1):
            click.echo(f"  {i}. {path.name} ({year})")

        choice = click.prompt(
            "Select folder number",
            type=click.IntRange(1, len(matches)),
        )
        project_path, year = matches[choice - 1]

    # Confirm with user
    click.echo(f"Found: {project_path.name} ({year})")
    if not click.confirm("Use this folder?", default=True):
        click.echo("Aborted.")
        return

    # Find or create 07-VO folder
    vo_parent = project_path / "07-VO"
    vo_parent.mkdir(exist_ok=True)

    # Clean up legacy empty 00-Arc folder if exists
    legacy_arc = vo_parent / "00-Arc"
    if legacy_arc.exists() and legacy_arc.is_dir() and not any(legacy_arc.iterdir()):
        legacy_arc.rmdir()
        click.echo("Removed empty legacy folder: 07-VO/00-Arc")

    # List existing VO folders
    existing_vos = sorted(
        [
            f.name
            for f in vo_parent.iterdir()
            if f.is_dir() and re.match(r"^\d{2}-VO\b", f.name)
        ]
    )
    if existing_vos:
        click.echo("Existing VO folders:")
        for vo_name_existing in existing_vos:
            click.echo(f"  {vo_name_existing}")
    else:
        click.echo("No existing VO folders.")

    # Get next VO number
    vo_number = get_next_vo_number(vo_parent)

    # Get VO name with explanation
    click.echo(f"New folder will be named: {vo_number:02d}-VO <your input>")
    vo_name = click.prompt("Please enter VO name")
    vo_name = vo_name.strip().upper()

    vo_folder_name = f"{vo_number:02d}-VO {vo_name}"
    vo_path = vo_parent / vo_folder_name

    if vo_path.exists():
        click.echo(f"Folder '{vo_folder_name}' already exists.")
        return

    # Create the VO folder and structure
    click.echo(f"Creating: 07-VO/{vo_folder_name}")
    vo_path.mkdir()
    create_vo_structure(vo_path)
    click.echo("Created folder structure successfully.")

    # Create new commercial Proposal
    if click.confirm("Do you want to create a new Commercial Proposal?"):
        from util import excelx

        version = click.prompt("Version No, default:", default="R0", show_default=True)
        version = str(version).upper()

        # VO number prefix (e.g., "V1" for 01-VO)
        vo_prefix = f"V{vo_number}"

        template_folder = (
            Path(RFQ).expanduser().parent.absolute().resolve() / "@tools/resources"
        )
        template = "Template.xlsx"
        commercial_folder = vo_path / "01-Commercial"

        # Filename: "<project_name> <vo_name> V1-R0.xlsx"
        commercial_file = f"{project_path.name} {vo_name} {vo_prefix}-{version}.xlsx"

        # Jobcode: "J12789 V1"
        jobcode = f"{project_path.name.split()[0]} {vo_prefix}"

        excelx.create_excel_from_template(
            template_folder,
            template,
            commercial_folder,
            commercial_file,
            jobcode,
            version,
        )

    # Ask to open folder
    if click.confirm("Do you want to open the VO folder?", default=True):
        open_with_default_app(vo_path)


@click.command()
@click.argument("folder_name", default="")
def ho(folder_name: str) -> None:
    """
    Handover project folders from @rfqs to @handover.

    Syncs project or VO folders for handover after successful bidding.
    """
    # Handle case where @rfqs or @handover does not exist
    if not Path(RFQ).expanduser().exists():
        click.echo("The folder @rfqs does not exist. Check if you have access.")
        return

    if not Path(HO).expanduser().exists():
        click.echo("The folder @handover does not exist. Check if you have access.")
        return

    # Get project folder name/job code
    if folder_name == "":
        folder_name = click.prompt("Please enter project folder name or job code")

    # Search for matching folders
    matches = find_project_folder(folder_name)

    if not matches:
        click.echo(f"No project folder found matching '{folder_name}'")
        return

    # Handle multiple matches
    if len(matches) == 1:
        project_path, year = matches[0]
    else:
        click.echo("Multiple folders found:")
        for i, (path, year) in enumerate(matches, 1):
            click.echo(f"  {i}. {path.name} ({year})")

        choice = click.prompt(
            "Select folder number",
            type=click.IntRange(1, len(matches)),
        )
        project_path, year = matches[choice - 1]

    # Confirm with user
    click.echo(f"Found: {project_path.name} ({year})")
    if not click.confirm("Use this folder?", default=True):
        click.echo("Aborted.")
        return

    # Get handover candidates
    candidates = get_handover_candidates(project_path)

    if len(candidates) == 1:
        # Only main folder available
        selected_name, source_path = candidates[0]
        click.echo("Handover candidate: 00-MAIN (Main Project)")
        if not click.confirm("Proceed with this folder?", default=True):
            click.echo("Aborted.")
            return
    else:
        click.echo("Handover candidates:")
        for i, (name, _) in enumerate(candidates, 1):
            label = "(Main Project)" if name == "00-MAIN" else ""
            click.echo(f"  {i}. {name} {label}")

        choice = click.prompt(
            "Select folder to handover",
            type=click.IntRange(1, len(candidates)),
        )
        selected_name, source_path = candidates[choice - 1]

    # Determine if this is a VO handover
    is_vo = selected_name != "00-MAIN"

    # Prepare destination in @handover
    handover_root = Path(HO).expanduser()
    project_dest = handover_root / project_path.name
    dest_path = project_dest / selected_name

    # Check for legacy folder structure
    if dest_path.exists() and not is_conforming_handover_folder(dest_path):
        click.echo("\nWarning: Destination folder exists with legacy structure:")
        click.echo(f"  {dest_path}")
        click.echo("Syncing may override existing content.")
        if not click.confirm("Do you want to continue?", default=False):
            click.echo("Aborted.")
            return

    click.echo(f"\nSyncing to: {dest_path}")

    # Perform the sync
    perform_handover_sync(source_path, dest_path, is_vo)

    click.echo("\nHandover sync complete.")
    click.echo("NOTE: Please update 05-Cost folder manually.")

    # Ask to open folder
    if click.confirm("Do you want to open the handover folder?", default=True):
        open_with_default_app(dest_path)


@click.command()
@click.argument("folder_name", default="")
def co(folder_name: str) -> None:
    """
    Create costing folder structure in @costing for a project.

    Creates folder for manual placement of costing files after successful bidding.
    """
    # Handle case where @rfqs or @costing does not exist
    if not Path(RFQ).expanduser().exists():
        click.echo("The folder @rfqs does not exist. Check if you have access.")
        return

    if not Path(CO).expanduser().exists():
        click.echo("The folder @costing does not exist. Check if you have access.")
        return

    # Get project folder name/job code
    if folder_name == "":
        folder_name = click.prompt("Please enter project folder name or job code")

    # Search for matching folders
    matches = find_project_folder(folder_name)

    if not matches:
        click.echo(f"No project folder found matching '{folder_name}'")
        return

    # Handle multiple matches
    if len(matches) == 1:
        project_path, year = matches[0]
    else:
        click.echo("Multiple folders found:")
        for i, (path, year) in enumerate(matches, 1):
            click.echo(f"  {i}. {path.name} ({year})")

        choice = click.prompt(
            "Select folder number",
            type=click.IntRange(1, len(matches)),
        )
        project_path, year = matches[choice - 1]

    # Confirm with user
    click.echo(f"Found: {project_path.name} ({year})")
    if not click.confirm("Use this folder?", default=True):
        click.echo("Aborted.")
        return

    # Get costing candidates (same as handover candidates)
    candidates = get_handover_candidates(project_path)

    if len(candidates) == 1:
        # Only main folder available
        selected_name, _ = candidates[0]
        click.echo("Costing candidate: 00-MAIN (Main Project)")
        if not click.confirm("Proceed with this folder?", default=True):
            click.echo("Aborted.")
            return
    else:
        click.echo("Costing candidates:")
        for i, (name, _) in enumerate(candidates, 1):
            label = "(Main Project)" if name == "00-MAIN" else ""
            click.echo(f"  {i}. {name} {label}")

        choice = click.prompt(
            "Select folder for costing",
            type=click.IntRange(1, len(candidates)),
        )
        selected_name, _ = candidates[choice - 1]

    # Prepare destination in @costing
    costing_root = Path(CO).expanduser()
    project_dest = costing_root / project_path.name
    dest_path = project_dest / selected_name

    # Create the folder
    if dest_path.exists():
        click.echo(f"Folder already exists: {dest_path}")
    else:
        dest_path.mkdir(parents=True, exist_ok=True)
        click.echo(f"\nCreated: {dest_path}")

    click.echo("Please copy costing files manually to this folder.")

    # Ask to open folder
    if click.confirm("Do you want to open the costing folder?", default=True):
        open_with_default_app(dest_path)


@click.group()
@click.help_option("-h", "--help")
@click.version_option(__version__, "-v", "--version", prog_name="bid")
def bid() -> None:
    "Utilities for bidding."
    pass


# Cast to Group to satisfy type checker (click.group decorator returns Group)
bid_group: click.Group = bid  # type: ignore[assignment]
bid_group.add_command(init)
bid_group.add_command(setup)
bid_group.add_command(clean)
bid_group.add_command(beautify)
bid_group.add_command(combine_pdf)
# Hidden alias for combine-pdf
cpdf_alias = click.Command(
    name="cpdf",
    callback=combine_pdf.callback,
    params=combine_pdf.params,
    hidden=True,
    help=combine_pdf.help,
)
bid_group.add_command(cpdf_alias)
bid_group.add_command(word2pdf)
bid_group.add_command(audit)
bid_group.add_command(vo)
bid_group.add_command(ho)
bid_group.add_command(co)

if __name__ == "__main__":
    bid()
