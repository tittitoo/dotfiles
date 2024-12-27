#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "click",
# "shpyx",
# ]
# ///

import click
import logging
import os
import shutil
import shpyx
from datetime import datetime
from pathlib import Path

RFQ = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@rfqs/"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def require_rename(file: str):
    "Check if file meets requried name specs"
    "If not, suggest renaming and the name"
    "Specs:"
    "No double 'space' or more"
    "No double '.' or more"
    "File extension must be lower case"
    "Remove RE, SV, FW at the start of email messages"
    "Remove orphan '_'"
    "Remove 'space' before file extension"
    "Remove detached '-' like ' -1' or ' -T'"
    pass


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
        else:
            click.echo("Folder creation aborted.")


@click.command()
@click.argument("folder_name", default="")
@click.option("-d", "--dry-run", is_flag=True, help="Dry run mode")
def clean(folder_name: str, dry_run: bool, start_path=RFQ) -> None:
    """
    Look for the folder in @rfqs and clean.
    """
    if folder_name == "":
        folder_name = click.prompt("Please enter folder name to clean")
    rfqs = Path(start_path).expanduser()
    folders = []
    for _, dirs, _ in os.walk(rfqs):
        for dir in dirs:
            folders.append(dir)
        dirs.clear()  # To stop at top level folder
        folders = [str(item) for item in folders if str(item).isdigit()]
        folders = sorted(folders, key=lambda x: int(x), reverse=True)

    # Walk files in the second level
    for level in folders:
        for _, dirs, _ in os.walk(rfqs / level):
            for dir in dirs:
                if folder_name == dir:
                    path = Path(rfqs / level / dir)
                    for root, dirs, files in os.walk(path):
                        if ".git" in dirs:
                            git_path = Path(rfqs / level / dir / ".git")
                            remove_folder(git_path)
                        # click.echo(f"{root}, {files}")
                        if dry_run:
                            for file in files:
                                click.echo(Path(root, file))
                    return
            dirs.clear()  # To stop at top level folder
    click.echo(f"{folder_name} cannot be found in {rfqs}")


@click.command()
def setup():
    """
    Setup necessary environment variables and alias
    """
    if os.name == "nt":
        click.echo("For Windows")
    else:
        pass
    pass


@click.command()
def audit():
    "Plan for audit features"
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
bid.add_command(test)
bid.add_command(clean)

if __name__ == "__main__":
    bid()
