"""
Audit module for tracking file contributions in SharePoint folders.

Supports three modes:
1. Local filesystem - basic stats (dates, sizes) without author info
2. SharePoint CSV import - full metadata from exported SharePoint data
3. m365 API - direct API access (requires admin consent)
"""

import csv
import json
import os
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import click


def is_sharepoint_folder(path: Path) -> bool:
    """Check if path is within a SharePoint/OneDrive sync folder."""
    path_str = str(path.resolve())
    sharepoint_indicators = [
        "SharePoint",
        "OneDrive",
        "Jason Electronics Pte Ltd",
    ]
    return any(indicator in path_str for indicator in sharepoint_indicators)


def check_m365_available() -> bool:
    """Check if m365 CLI is installed and user is logged in."""
    if not shutil.which("m365"):
        return False
    try:
        result = subprocess.run(
            ["m365", "status", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            status = json.loads(result.stdout)
            return status.get("logged", False)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        pass
    return False


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_date(timestamp: float) -> str:
    """Format timestamp to readable date."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def audit_local_filesystem(directory: Path) -> dict:
    """
    Audit a local directory using filesystem metadata.
    Returns stats without author information.
    """
    stats = {
        "mode": "local",
        "directory": str(directory),
        "total_files": 0,
        "total_size": 0,
        "by_extension": defaultdict(lambda: {"count": 0, "size": 0}),
        "by_month": defaultdict(lambda: {"count": 0, "size": 0}),
        "recent_files": [],
        "largest_files": [],
    }

    all_files = []

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                stat = file_path.stat()
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path.relative_to(directory)),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "created": getattr(stat, "st_birthtime", stat.st_ctime),
                }
                all_files.append(file_info)

                # Update totals
                stats["total_files"] += 1
                stats["total_size"] += stat.st_size

                # By extension
                ext = file_path.suffix.lower() or "(no extension)"
                stats["by_extension"][ext]["count"] += 1
                stats["by_extension"][ext]["size"] += stat.st_size

                # By month (based on modified date)
                month_key = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m")
                stats["by_month"][month_key]["count"] += 1
                stats["by_month"][month_key]["size"] += stat.st_size

            except (PermissionError, OSError):
                continue

    # Sort and get top files
    all_files.sort(key=lambda x: x["modified"], reverse=True)
    stats["recent_files"] = all_files[:10]

    all_files.sort(key=lambda x: x["size"], reverse=True)
    stats["largest_files"] = all_files[:10]

    return stats


def audit_sharepoint_csv(csv_path: Path) -> dict:
    """
    Parse SharePoint exported CSV/Excel file for audit data.
    Expected columns: Name, Modified, Modified By, Created, Created By
    """
    stats = {
        "mode": "sharepoint_import",
        "source_file": str(csv_path),
        "total_files": 0,
        "total_size": 0,
        "by_contributor": defaultdict(
            lambda: {"created": 0, "modified": 0, "last_active": None}
        ),
        "by_month": defaultdict(lambda: {"created": 0, "modified": 0}),
        "recent_activity": [],
        "files": [],
    }

    # Try to detect file format and parse
    suffix = csv_path.suffix.lower()

    if suffix == ".csv":
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    elif suffix in [".xlsx", ".xls"]:
        # Use pandas for Excel files
        import pandas as pd

        df = pd.read_excel(csv_path)
        rows = df.to_dict("records")
    else:
        raise click.ClickException(f"Unsupported file format: {suffix}")

    # Column name mapping (SharePoint uses various names)
    column_mappings = {
        "name": ["Name", "File Name", "FileName", "Title"],
        "modified": ["Modified", "Modified Date", "Last Modified"],
        "modified_by": ["Modified By", "Editor", "Last Modified By"],
        "created": ["Created", "Created Date", "Date Created"],
        "created_by": ["Created By", "Author"],
        "size": ["Size", "File Size", "FileSize"],
    }

    def find_column(row: dict, candidates: list) -> str | None:
        """Find the first matching column name."""
        for candidate in candidates:
            if candidate in row:
                return row[candidate]
            # Case-insensitive search
            for key in row:
                if key.lower() == candidate.lower():
                    return row[key]
        return None

    for row in rows:
        name = find_column(row, column_mappings["name"])
        if not name:
            continue

        modified_by = find_column(row, column_mappings["modified_by"])
        created_by = find_column(row, column_mappings["created_by"])
        modified = find_column(row, column_mappings["modified"])
        created = find_column(row, column_mappings["created"])
        size = find_column(row, column_mappings["size"])

        file_info = {
            "name": name,
            "modified_by": modified_by,
            "created_by": created_by,
            "modified": str(modified) if modified else None,
            "created": str(created) if created else None,
            "size": size,
        }
        stats["files"].append(file_info)
        stats["total_files"] += 1

        # Track by contributor
        if created_by:
            stats["by_contributor"][created_by]["created"] += 1
            if modified:
                current_last = stats["by_contributor"][created_by]["last_active"]
                if current_last is None or str(modified) > current_last:
                    stats["by_contributor"][created_by]["last_active"] = str(modified)

        if modified_by:
            stats["by_contributor"][modified_by]["modified"] += 1
            if modified:
                current_last = stats["by_contributor"][modified_by]["last_active"]
                if current_last is None or str(modified) > current_last:
                    stats["by_contributor"][modified_by]["last_active"] = str(modified)

        # Track by month (both created and modified)
        def parse_date_to_month(date_str):
            """Parse date string to YYYY-MM format."""
            if not date_str:
                return None
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    dt = datetime.strptime(str(date_str)[:10], fmt[:10])
                    return dt.strftime("%Y-%m")
                except ValueError:
                    continue
            return None

        created_month = parse_date_to_month(created)
        if created_month:
            stats["by_month"][created_month]["created"] += 1

        modified_month = parse_date_to_month(modified)
        if modified_month:
            stats["by_month"][modified_month]["modified"] += 1

    # Sort recent activity by created date
    stats["files"].sort(key=lambda x: x.get("created") or "", reverse=True)
    stats["recent_activity"] = stats["files"][:20]

    return stats


def print_local_report(stats: dict) -> None:
    """Print formatted report for local filesystem audit."""
    click.echo()
    click.echo(click.style("Local Folder Audit Report", fg="cyan", bold=True))
    click.echo(click.style("=" * 50, fg="cyan"))
    click.echo()
    click.echo(
        click.style("Note: ", fg="yellow")
        + "Local folder - author information not available"
    )
    click.echo()

    # Summary
    click.echo(click.style("Summary", fg="green", bold=True))
    click.echo(f"  Directory: {stats['directory']}")
    click.echo(f"  Total Files: {stats['total_files']}")
    click.echo(f"  Total Size: {format_size(stats['total_size'])}")
    click.echo()

    # By extension
    click.echo(click.style("Files by Extension", fg="green", bold=True))
    click.echo(f"  {'Extension':<15} {'Count':>8} {'Size':>12}")
    click.echo(f"  {'-' * 15} {'-' * 8} {'-' * 12}")
    sorted_ext = sorted(
        stats["by_extension"].items(), key=lambda x: x[1]["count"], reverse=True
    )
    for ext, data in sorted_ext[:10]:
        click.echo(f"  {ext:<15} {data['count']:>8} {format_size(data['size']):>12}")
    click.echo()

    # By month
    click.echo(click.style("Files by Month (Modified)", fg="green", bold=True))
    click.echo(f"  {'Month':<12} {'Count':>8} {'Size':>12}")
    click.echo(f"  {'-' * 12} {'-' * 8} {'-' * 12}")
    sorted_months = sorted(stats["by_month"].items(), reverse=True)
    for month, data in sorted_months[:12]:
        click.echo(f"  {month:<12} {data['count']:>8} {format_size(data['size']):>12}")
    click.echo()

    # Recent files
    click.echo(click.style("Recently Modified Files", fg="green", bold=True))
    click.echo(f"  {'Date':<12} {'Size':>10}  {'Name'}")
    click.echo(f"  {'-' * 12} {'-' * 10}  {'-' * 25}")
    for f in stats["recent_files"][:10]:
        date_str = format_date(f["modified"])
        size_str = format_size(f["size"])
        name = f["name"][:40] + "..." if len(f["name"]) > 40 else f["name"]
        click.echo(f"  {date_str:<12} {size_str:>10}  {name}")
    click.echo()


def print_sharepoint_report(stats: dict) -> None:
    """Print formatted report for SharePoint CSV import."""
    click.echo()
    click.echo(click.style("SharePoint Contribution Report", fg="cyan", bold=True))
    click.echo(click.style("=" * 60, fg="cyan"))
    click.echo()

    # Summary
    click.echo(click.style("Summary", fg="green", bold=True))
    click.echo(f"  Source: {stats['source_file']}")
    click.echo(f"  Total Files: {stats['total_files']}")
    click.echo(f"  Contributors: {len(stats['by_contributor'])}")
    click.echo()

    # By contributor
    click.echo(click.style("Contribution by User", fg="green", bold=True))
    click.echo(f"  {'Name':<25} {'Created':>10} {'Modified':>10} {'Last Active':<12}")
    click.echo(f"  {'-' * 25} {'-' * 10} {'-' * 10} {'-' * 12}")

    sorted_contributors = sorted(
        stats["by_contributor"].items(),
        key=lambda x: x[1]["created"] + x[1]["modified"],
        reverse=True,
    )
    for name, data in sorted_contributors:
        display_name = name[:25] if len(str(name)) > 25 else str(name)
        last_active = str(data["last_active"])[:10] if data["last_active"] else "-"
        click.echo(
            f"  {display_name:<25} {data['created']:>10} {data['modified']:>10} {last_active:<12}"
        )
    click.echo()

    # By month
    if stats["by_month"]:
        click.echo(click.style("Activity by Month", fg="green", bold=True))
        click.echo(f"  {'Month':<12} {'Files Created':>15} {'Files Modified':>15}")
        click.echo(f"  {'-' * 12} {'-' * 15} {'-' * 15}")
        sorted_months = sorted(stats["by_month"].items(), reverse=True)
        for month, data in sorted_months[:12]:
            click.echo(f"  {month:<12} {data['created']:>15} {data['modified']:>15}")
        click.echo()

    # Recent activity
    click.echo(click.style("Recent Activity", fg="green", bold=True))
    click.echo(f"  {'Created':<12} {'Created By':<25} {'File'}")
    click.echo(f"  {'-' * 12} {'-' * 25} {'-' * 40}")
    for f in stats["recent_activity"][:15]:
        created = str(f.get("created") or "-")[:10]
        by = str(f.get("created_by") or "-")[:25]
        name = f["name"]
        click.echo(f"  {created:<12} {by:<25} {name}")
    click.echo()


def export_to_csv(stats: dict, output_path: Path) -> None:
    """Export audit stats to CSV file."""
    if stats["mode"] == "local":
        # Export local stats
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Item", "Count", "Size"])

            # Extensions
            for ext, data in stats["by_extension"].items():
                writer.writerow(["Extension", ext, data["count"], data["size"]])

            # Months
            for month, data in stats["by_month"].items():
                writer.writerow(["Month", month, data["count"], data["size"]])

            # Recent files
            writer.writerow([])
            writer.writerow(["Recent Files", "Name", "Modified", "Size"])
            for f in stats["recent_files"]:
                writer.writerow(["", f["name"], format_date(f["modified"]), f["size"]])

    elif stats["mode"] == "sharepoint_import":
        # Export SharePoint stats
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Contributors summary
            writer.writerow(
                ["Contributor", "Files Created", "Files Modified", "Last Active"]
            )
            for name, data in stats["by_contributor"].items():
                writer.writerow(
                    [name, data["created"], data["modified"], data["last_active"]]
                )

            writer.writerow([])

            # All files
            writer.writerow(["File Name", "Created By", "Modified By", "Modified Date"])
            for f in stats["files"]:
                writer.writerow(
                    [
                        f["name"],
                        f.get("created_by", ""),
                        f.get("modified_by", ""),
                        f.get("modified", ""),
                    ]
                )

    click.echo(f"Report exported to: {output_path}")


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
    help="Fetch from SharePoint URL using browser session",
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
def audit(
    directory: str,
    import_file: str | None,
    output_file: str | None,
    api: bool,
    fetch_url: str | None,
    library: str,
    folder: str,
    debug: bool,
):
    """
    Audit folder to track file contributions.

    \b
    Modes:
      1. Local filesystem (default) - basic stats without author info
      2. SharePoint CSV import (-i) - full metadata from exported data
      3. SharePoint fetch (-f) - fetch directly using browser session
      4. m365 API (--api) - direct API access (requires admin consent)

    \b
    Examples:
      bid audit                     # Audit @docs folder
      bid audit /path/to/folder     # Audit specific folder
      bid audit -i export.csv       # Import SharePoint export
      bid audit -o report.csv       # Export to CSV
      bid audit -f https://company.sharepoint.com/sites/Site --folder "@docs"
    """
    # Fetch mode - get data from SharePoint via browser
    if fetch_url:
        from util.sharepoint_fetch import fetch_sharepoint_files, save_to_csv

        # Use chromium by default
        browser_type = "chromium"

        files = fetch_sharepoint_files(
            site_url=fetch_url,
            library=library,
            folder=folder,
            browser_type=browser_type,
            headless=not debug,
            debug=debug,
        )

        if not files:
            click.echo("No files found")
            return

        # Save to temp CSV and process
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)

        save_to_csv(files, tmp_path)

        # Now process as import
        stats = audit_sharepoint_csv(tmp_path)
        print_sharepoint_report(stats)

        if output_file:
            export_to_csv(stats, Path(output_file))

        # Cleanup temp file
        tmp_path.unlink(missing_ok=True)
        return

    # Import mode
    if import_file:
        csv_path = Path(import_file)
        click.echo(f"Importing from: {csv_path}")
        stats = audit_sharepoint_csv(csv_path)
        print_sharepoint_report(stats)

        if output_file:
            export_to_csv(stats, Path(output_file))
        return

    # Determine directory
    if directory:
        target_dir = Path(directory).expanduser().resolve()
    else:
        # Default to DOCS folder based on user
        import getpass

        username = getpass.getuser()
        if username == "oliver":
            docs_path = "~/OneDrive - Jason Electronics Pte Ltd/Shared Documents/@docs/"
        else:
            docs_path = "~/Jason Electronics Pte Ltd/Bid Proposal - Documents/@docs/"
        target_dir = Path(docs_path).expanduser()

    if not target_dir.exists():
        raise click.ClickException(f"Directory not found: {target_dir}")

    click.echo(f"Auditing: {target_dir}")

    # API mode
    if api:
        if not check_m365_available():
            raise click.ClickException(
                "m365 CLI not available or not logged in.\n"
                "Install: pnpm install -g @pnp/cli-microsoft365\n"
                "Login: m365 login"
            )
        # TODO: Implement m365 API mode
        click.echo("m365 API mode not yet implemented. Use --import-file instead.")
        return

    # Local filesystem mode
    is_sp = is_sharepoint_folder(target_dir)
    if is_sp:
        click.echo(
            click.style("Tip: ", fg="yellow")
            + "For author info, export from SharePoint and use: bid audit -i export.csv"
        )

    stats = audit_local_filesystem(target_dir)
    print_local_report(stats)

    if output_file:
        export_to_csv(stats, Path(output_file))


if __name__ == "__main__":
    audit()
