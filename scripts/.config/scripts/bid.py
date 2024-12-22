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
import shpyx
from datetime import datetime
from pathlib import Path

RFQ = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@rfqs/"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Create project folder structure
@click.command()
@click.argument("folder_name")
def init(folder_name):
    """Create fodler structure for project"""
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
        new_path.mkdir()
        itb = new_path / "00-ITB/00-Arc"
        itb.mkdir(parents=True, exist_ok=True)
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


@click.command()
def test():
    shpyx.run("echo hello world | pbcopy")


@click.group()
def bid():
    pass


bid.add_command(init)
bid.add_command(test)


if __name__ == "__main__":
    bid()
