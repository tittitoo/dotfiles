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
