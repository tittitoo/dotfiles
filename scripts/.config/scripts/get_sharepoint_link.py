#!/usr/bin/env -S uv run --quiet --no-upgrade --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click",
# ]
# ///
"""
Convert local OneDrive-synced file/folder paths to SharePoint web URLs
and copy to clipboard.

Usage:
    uv run get_sharepoint_link.py <path>
    uv run get_sharepoint_link.py <path> --no-copy
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import quote

import click


def build_sharepoint_url(host: str, relative_path: Path, is_file: bool) -> str:
    """Build SharePoint shared library URL."""
    type_prefix = ":b:" if is_file else ":f:"
    encoded_path = quote(str(relative_path), safe="/@")
    return f"{host}/{type_prefix}/r/sites/BidProposal2/Shared%20Documents/{encoded_path}?csf=1&web=1"


def build_personal_onedrive_url(host: str, relative_path: Path, is_file: bool) -> str:
    """Build personal OneDrive URL."""
    encoded_path = quote(f"/personal/thiha_jason_com_sg/Documents/{relative_path}", safe="")
    return f"{host}/my?id={encoded_path}"


@dataclass
class OneDriveConfig:
    name: str
    root: Path
    host: str
    build_url: Callable[[str, Path, bool], str]


ONEDRIVE_CONFIGS = [
    OneDriveConfig(
        name="SharePoint Bid Proposal",
        root=Path.home() / "Library/CloudStorage/OneDrive-SharedLibraries-JasonElectronicsPteLtd/Bid Proposal - Documents",
        host="https://jasonmarine.sharepoint.com",
        build_url=build_sharepoint_url,
    ),
    OneDriveConfig(
        name="Personal OneDrive",
        root=Path.home() / "Library/CloudStorage/OneDrive-JasonElectronicsPteLtd",
        host="https://jasonmarine-my.sharepoint.com",
        build_url=build_personal_onedrive_url,
    ),
]


def get_sharepoint_url(local_path: str) -> str | None:
    """Convert a local OneDrive path to SharePoint/OneDrive URL.

    Args:
        local_path: Path to a file or folder in the OneDrive sync folder.

    Returns:
        SharePoint/OneDrive URL or None if path is not in OneDrive.
    """
    path = Path(local_path).resolve()

    for config in ONEDRIVE_CONFIGS:
        try:
            relative_path = path.relative_to(config.root)
            is_file = path.is_file()
            return config.build_url(config.host, relative_path, is_file)
        except ValueError:
            continue

    return None


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using pbcopy.

    Args:
        text: Text to copy to clipboard.

    Returns:
        True if successful, False otherwise.
    """
    try:
        process = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            text=True,
        )
        process.communicate(input=text)
        return process.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--no-copy", is_flag=True, help="Print URL without copying to clipboard")
def main(path: str, no_copy: bool) -> None:
    """Convert local OneDrive path to SharePoint URL and copy to clipboard."""
    url = get_sharepoint_url(path)

    if url is None:
        click.echo(f"Error: Path is not in a supported OneDrive folder: {path}", err=True)
        raise SystemExit(1)

    if no_copy:
        click.echo(url)
        return

    if copy_to_clipboard(url):
        click.echo(f"Copied to clipboard: {url}")
    else:
        click.echo("Failed to copy to clipboard. URL:", err=True)
        click.echo(url)


if __name__ == "__main__":
    main()
