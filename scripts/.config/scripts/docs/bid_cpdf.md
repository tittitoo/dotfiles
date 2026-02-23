## `bid cpdf --create-manifest` / `-c`

Recursively finds all PDF files in the current directory and produces a
`manifest.md` file. The manifest is intended as a draft input for `bid cpdf -m`.

**Output format:**

```markdown
# <current folder name>

- relative/path/to/file.pdf
- subfolder/another.pdf
```

- Files are sorted alphabetically by relative path.
- `00-Combined.pdf` is excluded automatically.
- The `# Title` line becomes the output PDF filename when passed to `bid cpdf -m`.

**Typical workflow:**

```bash
bid cpdf -c          # generate manifest.md draft
# edit manifest.md: reorder, remove unwanted files, adjust title
bid cpdf -m          # combine using the manifest
```
