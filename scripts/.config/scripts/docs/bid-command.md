# Bid Command Reference

Command-line tool for bid proposal management.

## Installation

After setup, run commands using:

```bash
bid <command> [options]
```

Run `bid setup` to configure shell aliases.

| Global option    | Description          |
| ---------------- | -------------------- |
| `-h, --help`     | Show help            |
| `-v, --version`  | Show version         |

---

## Commands

### `init`

Create project folder structure in `@rfqs`.

```bash
bid init <folder_name>
```

Creates the following structure under `@rfqs/<year>/<folder_name>/`:

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

Prompts to optionally create a Commercial Proposal Excel file from template.

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

### `combine-pdf` / `cpdf`

Merge PDFs in current directory.

```bash
bid combine-pdf [options]
bid cpdf [options]        # alias
```

| Option                  | Description                                    |
| ----------------------- | ---------------------------------------------- |
| `-o, --outline`         | Add bookmarks from filenames                   |
| `-t, --toc`             | Add table of contents page                     |
| `-m, --manifest`        | Use manifest file for custom order             |
| `-c, --create-manifest` | Create `manifest.md` from all PDFs (recursive) |
| `-y, --yes`             | Skip confirmation prompts                      |

**Default output:** `00-Combined.pdf`

#### Creating a Manifest

Use `-c` to auto-generate a `manifest.md` draft from all PDFs in the current
directory (recursive). Edit it, then run with `-m` to combine.

```bash
bid cpdf -c      # generates manifest.md
# edit manifest.md as needed
bid cpdf -m      # combine using the manifest
```

`00-Combined.pdf` is excluded automatically. Files are listed as relative paths,
sorted alphabetically.

#### Manifest File Format

Create or edit a `.md` or `.txt` file in the directory:

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

### `vo`

Create a Variation Order folder structure under an existing project.

```bash
bid vo <folder_name>
```

Searches for the project in `@rfqs`, then creates a numbered VO subfolder
inside `07-VO/` with the following structure:

```
07-VO/<nn>-VO <name>/
├── 00-ITB/<date>/
├── 01-Commercial/00-Arc/
├── 02-Technical/00-Arc/
├── 03-Supplier/00-Arc/
├── 04-Datasheet/00-Arc/
└── 05-PO/00-Arc/
```

VO folders are numbered automatically (01-VO, 02-VO, …).
Prompts to optionally create a Commercial Proposal Excel file from template.

---

### `ho`

Handover project or VO folders from `@rfqs` to `@handover`.

```bash
bid ho <folder_name>
```

Performs a one-way mirror sync. Searches for the project in `@rfqs`, lets you
select the main project or a specific VO, then syncs to `@handover/<project>/`.

**Folder mapping:**

| Source (main)  | Source (VO) | Destination    |
| -------------- | ----------- | -------------- |
| `00-ITB`       | `00-ITB`    | `00-ITB`       |
| `06-PO`        | `05-PO`     | `01-PO`        |
| `02-Technical` | `02-Technical` | `02-Technical` |
| `03-Supplier`  | `03-Supplier`  | `03-Supplier`  |
| `04-Datasheet` | `04-Datasheet` | `04-Datasheet` |
| `05-Drawing`   | `05-Drawing`   | `06-Drawing`   |
| —              | —           | `05-Cost` (created empty) |

`05-Cost` must be populated manually after handover.

---

### `co`

Create a costing folder in `@costing` for a project.

```bash
bid co <folder_name>
```

Searches for the project in `@rfqs`, lets you select the main project or a
specific VO, then creates the destination folder in `@costing/<project>/`.
Files must be copied manually.

---

### `audit`

Track file contributions in a folder.

```bash
bid audit [directory] [options]
```

| Option              | Description                                           |
| ------------------- | ----------------------------------------------------- |
| `-f, --fetch URL`   | Fetch from SharePoint URL (recommended)               |
| `-l, --library`     | SharePoint library title (default: Documents)         |
| `--folder`          | Folder path within library (e.g., `@docs`)            |
| `--month`           | Filter by month: `YYYY-MM` or range `YYYY-MM:YYYY-MM` |
| `--all-time`        | Show all data without time filtering                  |
| `--person NAME`     | Filter to specific person (or `all` for everyone)     |
| `-i, --import-file` | Import from SharePoint exported CSV/Excel             |
| `-o, --output`      | Export report to CSV file                             |
| `--debug`           | Show browser window (for troubleshooting)             |

**Default:** Audits local `@docs` folder (no author info). When fetching from
SharePoint, defaults to current month and shows interactive contributor selection.

#### Modes

1. **Local filesystem** (default) — basic stats without author info
2. **SharePoint fetch** (`-f`) — fetch via browser automation (recommended)
3. **SharePoint import** (`-i`) — import from exported CSV/Excel

#### Examples

```bash
# Local folder audit (no author info)
bid audit
bid audit /path/to/folder

# Fetch from SharePoint (recommended - includes author info)
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

Default applies smart column width (max 80 chars, word wrap).

---

### `word2pdf`

Batch convert Word documents to PDF in the current directory.

```bash
bid word2pdf [options]
```

| Option      | Description               |
| ----------- | ------------------------- |
| `-y, --yes` | Skip confirmation prompts |

Converts all `.docx` files. Requires Microsoft Word to be installed.

---

### `setup`

Configure environment and shell aliases.

```bash
bid setup
```

Installs dependencies, configures xlwings, copies Excel templates, and adds
the `bid` alias to your shell configuration.
