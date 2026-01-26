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
from pathlib import Path
from urllib.parse import quote

import click

# Configuration mapping
ONEDRIVE_ROOT = (
    Path.home()
    / "Library/CloudStorage/OneDrive-SharedLibraries-JasonElectronicsPteLtd/Bid Proposal - Documents"
)
SHAREPOINT_HOST = "https://jasonmarine.sharepoint.com"
SHAREPOINT_SITE_PATH = "/sites/BidProposal2/Shared%20Documents"


def get_sharepoint_url(local_path: str) -> str | None:
    """Convert a local OneDrive path to SharePoint URL.

    Args:
        local_path: Path to a file or folder in the OneDrive sync folder.

    Returns:
        SharePoint URL or None if path is not in OneDrive.
    """
    path = Path(local_path).resolve()

    try:
        relative_path = path.relative_to(ONEDRIVE_ROOT)
    except ValueError:
        return None

    # Determine if path is a file or folder for SharePoint routing
    # :f: = folder, :b: = file
    type_prefix = ":b:" if path.is_file() else ":f:"

    # URL-encode the path, preserving / and @ (matching Finder's behavior)
    encoded_path = quote(str(relative_path), safe="/@")

    return f"{SHAREPOINT_HOST}/{type_prefix}/r{SHAREPOINT_SITE_PATH}/{encoded_path}?csf=1&web=1"


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
        click.echo(f"Error: Path is not in OneDrive folder: {path}", err=True)
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
