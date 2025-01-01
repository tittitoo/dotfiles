#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "click",
# "shpyx",
# ]
# ///

import logging
import os
import platform
import re
import shutil
from datetime import datetime
from pathlib import Path

import click
import shpyx

RFQ = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@rfqs/"
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


def open_with_default_app(file_path: Path):
    "Open file_path with default application"
    if platform.system() == "Windows":
        try:
            click.launch("file://" + str(file_path.resolve()))
            # shpyx.run(f'explorer.exe "{file_path}"')
        except Exception as _:
            click.echo("Not yet implemented.")
    elif platform.system() == "Darwin":
        click.launch("file://" + str(file_path.resolve()))
        # shpyx.run(f"open '{file_path}'")
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
    Check if file meets requried name specs
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
    new_file_name = re.sub(r"-{2,}", "-", new_file_name)
    new_file_name = re.sub(r"_{2,}", "_", new_file_name)
    new_file_name = re.sub(r" \.+ ", " ", new_file_name)
    new_file_name = re.sub(r" _(\w+)", r" \1", new_file_name)
    new_file_name = re.sub(r"(#+|_+\s{1,})", r" ", new_file_name)
    new_file_name = re.sub(r"(\[+)", "", new_file_name)
    new_file_name = re.sub(r"(\]+)", "", new_file_name)
    new_file_name = re.sub(r"^(RE(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(SV(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
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
    new_file_name = re.sub(r"^(FWD(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(FW(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(SV(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
    new_file_name = re.sub(r"^(RE(_+|\s{1,}))", "", new_file_name, flags=re.IGNORECASE)
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
    if folder_name == "":
        folder_name = click.prompt("Please enter folder name to create")
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
        if click.confirm("Do you want to open the folder?", abort=True):
            open_with_default_app(new_path)
    else:
        if click.confirm(f"'{new_path}' will be created. Continue?", abort=True):
            new_path.mkdir()
            itb = new_path / "00-ITB/00-Arc"
            itb.mkdir(parents=True, exist_ok=True)
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
            vo = new_path / "07-VO/00-Arc"
            vo.mkdir(parents=True, exist_ok=True)
            toolkit = new_path / "08-Toolkit/00-Arc"
            toolkit.mkdir(parents=True, exist_ok=True)
            click.echo(f"Created fodler {new_path}")
            if click.confirm(
                "Do you want to open the folder?",
                abort=True,
            ):
                open_with_default_app(new_path)
        else:
            click.echo("Folder creation aborted.")


@click.command()
@click.argument("folder_name", default="")
@click.option("-d", "--dry-run", is_flag=True, help="Dry run mode")
@click.option(
    "-r",
    "--remove-git",
    is_flag=True,
    help="Delete .git folder and .gitignore if exists",
)
def clean(folder_name: str, dry_run: bool, remove_git: bool) -> None:
    """
    Clean files in folder. Default search path is @rfqs.
    If folder is given, clean the folder.
    If not, search the folder in @rfqs and clean.
    """
    if folder_name == "":
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
        clean_folder(Path.cwd(), dry_run=dry_run)
    else:
        clean_rfqs(folder_name, remove_git=remove_git, dry_run=dry_run)


def clean_folder(start_path, dry_run=False):
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
        if click.confirm("Do you want to rename the files?", abort=True):
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
    Setup necessary environment variables and alias
    """
    if platform.system() == "Linux":
        pass
    elif platform.system() == "Windows":
        """
        Add alias for shell `uv run bid.py` -> `bid`
        Check and confirm the location for `RFQ`
        Add `@tools` folder to PATH
        I may consider Git BASH as the default shell
        """
        pass
    elif platform.system() == "Darwin":
        pass
    else:
        pass


@click.command()
def audit():
    "Plan for audit features"
    pass


@click.command()
def beautify():
    "Plan for beautify features"
    pass


@click.command()
def test():
    shpyx.run("echo hello world | pbcopy")


@click.group()
def bid():
    "Utilities for bidding."
    pass


bid.add_command(init)
bid.add_command(setup)
# bid.add_command(test)
bid.add_command(clean)

if __name__ == "__main__":
    bid()
