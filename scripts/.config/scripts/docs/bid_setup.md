# `bid setup`

@bid.py

## For Windows

### Bootstrap (`setup.bat`)

`setup.bat` must be run first (double-click). It handles the chicken-and-egg
problem: `bid.py` requires `uv` to run, but `setup()` lives inside `bid.py`.

1. Install `uv` if it is not already installed in user's computer. The
   PowerShell command for installation is:
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Refresh PATH from registry so the newly installed `uv` is available in the
   current session.
3. Run `uv run bid.py setup`.

### `bid setup` (steps in bid.py)

1. Create a folder called '.managed_python' in user's home folder.
2. Copy over 'pyproject.toml' file from @tools folder pointed to by TOOLS into this folder.
3. Run `uv sync` in this folder to set up .venv environment.
4. Add python from this .venv environment to user's PATH. Note that user
   does not have admin access to the computer. Move this PATH variable to
   the top of the list so that when the script look for python, it finds this
   first instead of other python system may have pre-installed.
5. Install xlwings add-in via `xlwings addin install`. If Excel is running,
   request user's permission to kill Excel first.
6. Copy over 'PERSONAL.XLSB' file from @tools folder to user's XLSTART
   folder. If the file already exists, override it.
7. When Excel starts, 'PERSONAL.XLSB' needs to be opened in a hidden state.
   This is handled by VBA in PERSONAL.XLSB's ThisWorkbook module (pre-configured).
8. Make .managed_python folder hidden in Windows.
9. Set xlwings interpreter path to .managed_python/.venv python.
10. Set xlwings PYTHONPATH to @tools folder and disable ADD_WORKBOOK_TO_PYTHONPATH.
11. Copy `Excel.officeUI` from @tools/resources to
    `~\AppData\Local\Microsoft\Office`. This sets up the Excel ribbon
    customizations tied to PERSONAL.XLSB macros. Overrides if the file exists.
