# Bid Command Reference

Command-line tool for bid proposal management.

## Installation

After setup, run commands using:

```bash
bid <command> [options]
```

Run `bid setup` to configure shell aliases.

---

## Commands

### `init`

Create project folder structure in `@rfqs`.

```bash
bid init <folder_name>
```

Creates the following structure:

```
<folder_name>/
├── 00-ITB/<date>/
├── 01-Commercial/00-Arc/
├── 02-Technical/00-Arc/
├── 03-Supplier/00-Arc/
├── 04-Datasheet/00-Arc/
├── 05-Drawing/00-Arc/
├── 06-PO/00-Arc/
├── 07-VO/
└── 08-Toolkit/00-Arc/
```

---

### `clean`

Normalize file names in a folder.

```bash
bid clean <folder_name> [options]
```

| Option             | Description                           |
| ------------------ | ------------------------------------- |
| `-d, --dry-run`    | Preview changes without applying      |
| `-y, --yes`        | Skip confirmation prompts             |
| `-r, --remove-git` | Remove `.git` folder and `.gitignore` |

**What it cleans:**

- Email prefixes (RE:, FW:, FWD:, EXTERNAL, URGENT)
- Uppercase extensions → lowercase
- Multiple dashes/underscores → single
- Brackets and extra whitespace

---

### `combine-pdf`

Merge PDFs in current directory.

```bash
bid combine-pdf [options]
```

| Option           | Description                        |
| ---------------- | ---------------------------------- |
| `-o, --outline`  | Add bookmarks from filenames       |
| `-t, --toc`      | Add table of contents page         |
| `-m, --manifest` | Use manifest file for custom order |
| `-y, --yes`      | Skip confirmation prompts          |

**Default output:** `00-Combined.pdf`

#### Using Manifest Mode

Create a `.md` or `.txt` file in the directory:

```markdown
# Output Filename

## Section Title

- file1.pdf
- file2.pdf

## Another Section

- file3.pdf
```

- `# Title` → Output filename
- `## Section` → Bookmark heading
- `- file.pdf` → Files to include (searches locally, then `@docs`)

---

### `audit`

Track file contributions in a folder.

```bash
bid audit [directory] [options]
```

| Option              | Description                                         |
| ------------------- | --------------------------------------------------- |
| `-f, --fetch`       | Fetch from SharePoint URL (recommended)             |
| `-l, --library`     | SharePoint library title (default: Documents)       |
| `--folder`          | Folder path within library (e.g., '@docs')          |
| `--month`           | Filter by month: `YYYY-MM` or range `YYYY-MM:YYYY-MM` |
| `--all-time`        | Show all data without time filtering                |
| `--person NAME`     | Filter to specific person (or 'all' for everyone)   |
| `-i, --import-file` | Import from SharePoint exported CSV/Excel           |
| `-o, --output`      | Export report to CSV file                           |
| `--debug`           | Show browser window (for troubleshooting)           |

**Default:** Audits local `@docs` folder (no author info). When fetching from SharePoint, defaults to current month and shows interactive contributor selection.

#### Modes

1. **Local filesystem** (default) - basic stats without author info
2. **SharePoint fetch** (`-f`) - fetch via browser automation (recommended)
3. **SharePoint import** (`-i`) - import from exported CSV/Excel

#### Examples

```bash
# Local folder audit (no author info)
bid audit
bid audit /path/to/folder

# Fetch from SharePoint (recommended - includes author info)
# Default: current month, interactive person selection
bid audit -f https://company.sharepoint.com/sites/Site --folder "@docs"

# All contributors, current month
bid audit -f URL --folder "@docs" --person all

# Specific month
bid audit -f URL --folder "@docs" --month 2025-12

# Month range (January to June 2025)
bid audit -f URL --folder "@docs" --month 2025-01:2025-06

# All time (no month filter)
bid audit -f URL --folder "@docs" --all-time

# Specific person, all time
bid audit -f URL --folder "@docs" --person "John Doe" --all-time

# Import from exported file
bid audit -i sharepoint.csv
bid audit -i export.xlsx -o report.csv
```

#### Setup for SharePoint Fetch

Requires Playwright (one-time setup):

```bash
# Install Playwright
pip install playwright

# Install browser (one-time)
playwright install chromium
```

**First run:** Browser window opens for Microsoft login. Session is saved for future runs.

**Subsequent runs:** Runs headless (no browser window) using saved session.

---

### `beautify`

Apply formatting to Excel files.

```bash
bid beautify <excel_file> [options]
```

| Option       | Description                                   |
| ------------ | --------------------------------------------- |
| `-f, --font` | Apply font formatting only (skip smart width) |

---

### `word2pdf`

Batch convert Word documents to PDF.

```bash
bid word2pdf [options]
```

| Option      | Description               |
| ----------- | ------------------------- |
| `-y, --yes` | Skip confirmation prompts |

Converts all `.docx` files in current directory.

---

### `setup`

Configure environment and shell aliases.

```bash
bid setup
```

Adds the `bid` alias to your shell configuration.
