#!/usr/bin/env python3
"""
Fetch SharePoint document library metadata using Playwright browser automation.

Uses existing browser session to authenticate, avoiding the need for
admin consent or app registration.

Dependencies:
    pip install playwright
    playwright install chromium  # one-time browser install
"""

import csv
import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse, quote

import click

# Session storage location
SESSION_DIR = Path.home() / ".config" / "bid" / "sharepoint-session"


def get_session_dir(browser_type: str = "chromium") -> Path:
    """Get the session directory for persistent browser context."""
    session_path = SESSION_DIR / browser_type
    session_path.mkdir(parents=True, exist_ok=True)
    return session_path


def fetch_sharepoint_files(
    site_url: str,
    library: str,
    folder: str = "",
    browser_type: str = "chromium",
    headless: bool = True,
    debug: bool = False,
) -> list[dict]:
    """
    Fetch file metadata from SharePoint document library using Playwright.

    Args:
        site_url: SharePoint site URL (e.g., https://company.sharepoint.com/sites/MySite)
        library: Document library name (e.g., "Shared Documents")
        folder: Subfolder path within library (e.g., "@docs")
        browser_type: Browser to use ("chromium" or "webkit" for Safari)
        headless: Run browser in headless mode (no window)
        debug: Debug mode - shows browser window and verbose output

    Returns:
        List of file metadata dicts
    """
    try:
        from playwright.sync_api import (
            sync_playwright,
            TimeoutError as PlaywrightTimeout,
        )
    except ImportError:
        raise click.ClickException(
            "Playwright is required. Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        )

    # Debug mode forces visible browser
    if debug:
        headless = False
        click.echo(f"Debug mode: browser window will be visible")

    session_dir = get_session_dir(browser_type)
    click.echo(f"Using session: {session_dir}")
    click.echo(f"Site: {site_url}")
    click.echo(f"Library: {library}")
    if folder:
        click.echo(f"Folder: {folder}")

    files = []

    with sync_playwright() as p:
        # Select browser
        if browser_type == "webkit":
            browser_engine = p.webkit
        else:
            browser_engine = p.chromium

        # Launch with persistent context (saves login session)
        context = browser_engine.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=headless,
            # Slower in debug mode for visibility
            slow_mo=100 if debug else 0,
        )

        try:
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to SharePoint site
            click.echo(f"Navigating to SharePoint...")
            page.goto(site_url, wait_until="networkidle", timeout=60000)

            # Check if we need to login
            current_url = page.url
            if (
                "login.microsoftonline.com" in current_url
                or "login.live.com" in current_url
            ):
                click.echo()
                click.echo(click.style("Login required!", fg="yellow", bold=True))
                click.echo("Please log in to Microsoft 365 in the browser window.")
                click.echo("Your session will be saved for future runs.")
                click.echo()

                # Wait for user to complete login (up to 5 minutes)
                try:
                    page.wait_for_url(
                        f"**{urlparse(site_url).netloc}**",
                        timeout=300000,  # 5 minutes
                    )
                    click.echo(click.style("Login successful!", fg="green"))
                except PlaywrightTimeout:
                    raise click.ClickException("Login timeout. Please try again.")

            # Build folder path
            # SharePoint stores paths like: /sites/SiteName/Shared Documents/FolderName
            site_path = urlparse(site_url).path  # e.g., /sites/BidProposal2
            library_url_path = "Shared Documents"  # URL path name

            if folder:
                # Use folder-based API to get files directly from the folder
                # This avoids the 5000 item limit issue when filtering library items
                folder_server_path = f"{site_path}/{library_url_path}/{folder}"
                encoded_folder_path = quote(folder_server_path, safe="/")

                # Get files from folder (and subfolders via recursive call)
                api_url = (
                    f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{encoded_folder_path}')/Files"
                    f"?$select=Name,ServerRelativeUrl,TimeCreated,TimeLastModified,Length,"
                    f"Author/Title,Author/EMail,ModifiedBy/Title,ModifiedBy/EMail"
                    f"&$expand=Author,ModifiedBy"
                )
                use_folder_api = True
            else:
                # No folder specified - use library items API
                folder_server_path = ""
                api_url = (
                    f"{site_url}/_api/web/lists/getbytitle('{library}')/items"
                    f"?$select=FileLeafRef,FileRef,Created,Modified,"
                    f"Author/Title,Author/EMail,Editor/Title,Editor/EMail,"
                    f"File/Length,File/TimeLastModified,FileDirRef"
                    f"&$expand=Author,Editor,File"
                    f"&$top=5000"
                    f"&$orderby=Modified desc"
                )
                use_folder_api = False

            click.echo(f"Fetching file metadata...")
            if debug:
                click.echo(f"API URL: {api_url}")

            # Execute the API call using the browser's authenticated session
            response = page.evaluate(
                """
                async (apiUrl) => {
                    try {
                        const response = await fetch(apiUrl, {
                            headers: {
                                'Accept': 'application/json;odata=verbose',
                                'Content-Type': 'application/json;odata=verbose'
                            },
                            credentials: 'include'
                        });

                        if (!response.ok) {
                            return { error: `HTTP ${response.status}: ${response.statusText}` };
                        }

                        const data = await response.json();
                        return { success: true, data: data };
                    } catch (e) {
                        return { error: e.message };
                    }
                }
                """,
                api_url,
            )

            if response.get("error"):
                raise click.ClickException(f"API Error: {response['error']}")

            results = response.get("data", {}).get("d", {}).get("results", [])
            click.echo(f"Found {len(results)} files")

            # Process results - handle both folder API and library items API formats
            for item in results:
                if use_folder_api:
                    # Folder API format
                    filename = item.get("Name", "")
                    if not filename:
                        continue
                    file_info = {
                        "Name": filename,
                        "Path": item.get("ServerRelativeUrl", ""),
                        "Created": item.get("TimeCreated", ""),
                        "Modified": item.get("TimeLastModified", ""),
                        "Created By": (
                            item.get("Author", {}).get("Title", "")
                            if item.get("Author")
                            else ""
                        ),
                        "Created By Email": (
                            item.get("Author", {}).get("EMail", "")
                            if item.get("Author")
                            else ""
                        ),
                        "Modified By": (
                            item.get("ModifiedBy", {}).get("Title", "")
                            if item.get("ModifiedBy")
                            else ""
                        ),
                        "Modified By Email": (
                            item.get("ModifiedBy", {}).get("EMail", "")
                            if item.get("ModifiedBy")
                            else ""
                        ),
                        "Size": item.get("Length", 0),
                    }
                else:
                    # Library items API format
                    filename = item.get("FileLeafRef")
                    if not filename:
                        continue
                    file_info = {
                        "Name": filename,
                        "Path": item.get("FileRef", ""),
                        "Created": item.get("Created", ""),
                        "Modified": item.get("Modified", ""),
                        "Created By": (
                            item.get("Author", {}).get("Title", "")
                            if item.get("Author")
                            else ""
                        ),
                        "Created By Email": (
                            item.get("Author", {}).get("EMail", "")
                            if item.get("Author")
                            else ""
                        ),
                        "Modified By": (
                            item.get("Editor", {}).get("Title", "")
                            if item.get("Editor")
                            else ""
                        ),
                        "Modified By Email": (
                            item.get("Editor", {}).get("EMail", "")
                            if item.get("Editor")
                            else ""
                        ),
                        "Size": (
                            item.get("File", {}).get("Length", 0)
                            if item.get("File")
                            else 0
                        ),
                    }
                files.append(file_info)

            if debug:
                click.echo(f"Processed {len(files)} files")

        finally:
            context.close()

    return files


def save_to_csv(files: list[dict], output_path: Path) -> None:
    """Save file metadata to CSV."""
    if not files:
        click.echo("No files to save")
        return

    fieldnames = [
        "Name",
        "Size",
        "Created",
        "Created By",
        "Modified",
        "Modified By",
        "Path",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(files)

    click.echo(f"Saved to: {output_path}")


def clear_session(browser_type: str = "chromium") -> None:
    """Clear saved browser session."""
    import shutil

    session_dir = get_session_dir(browser_type)
    if session_dir.exists():
        shutil.rmtree(session_dir)
        click.echo(f"Cleared session: {session_dir}")
    else:
        click.echo("No session to clear")


@click.command()
@click.argument("site_url")
@click.option(
    "-l",
    "--library",
    default="Documents",
    help="Document library title for API (default: Documents)",
)
@click.option(
    "-f",
    "--folder",
    default="",
    help="Folder path within the library (e.g., '@docs')",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="sharepoint_export.csv",
    help="Output CSV file path",
)
@click.option(
    "-b",
    "--browser",
    type=click.Choice(["chromium", "webkit"]),
    default="chromium",
    help="Browser to use: chromium (Chrome) or webkit (Safari)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Debug mode: show browser window, verbose output",
)
@click.option(
    "--clear-session",
    "clear",
    is_flag=True,
    help="Clear saved login session and exit",
)
def fetch(
    site_url: str,
    library: str,
    folder: str,
    output: str,
    browser: str,
    debug: bool,
    clear: bool,
):
    """
    Fetch SharePoint document library metadata using browser automation.

    \b
    First run will open a browser for Microsoft login.
    Session is saved for future runs (no re-login needed).

    \b
    Examples:
      # Fetch from @docs folder in Shared Documents library
      python sharepoint_fetch.py https://company.sharepoint.com/sites/MySite -f "@docs"

      # Fetch from a different library
      python sharepoint_fetch.py URL -l "Documents" -f "subfolder"

      # Use Safari instead of Chrome
      python sharepoint_fetch.py URL -f "@docs" -b webkit

      # Debug mode (shows browser)
      python sharepoint_fetch.py URL -f "@docs" --debug

      # Clear saved session
      python sharepoint_fetch.py URL --clear-session
    """
    if clear:
        clear_session(browser)
        return

    output_path = Path(output)

    files = fetch_sharepoint_files(
        site_url=site_url,
        library=library,
        folder=folder,
        browser_type=browser,
        headless=not debug,
        debug=debug,
    )

    if files:
        save_to_csv(files, output_path)
        click.echo()
        click.echo(f"Export complete: {len(files)} files")
        click.echo(f"Run 'bid audit -i {output}' to analyze the data")
    else:
        click.echo("No files found")


if __name__ == "__main__":
    fetch()
