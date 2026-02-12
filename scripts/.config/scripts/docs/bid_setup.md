# `bid setup`

@bid.py

## For Windows

1. Install `uv` if it is not already installed in user's computer. The
   power shell command for installation is:
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Create a folder called '.managed_python' in user's home folder.
3. Copy over 'pyproject.toml' file from @tools folder pointed to by TOOLS into this folder.
4. Run `uv sync` in this folder to set up .venv environment.
5. Add python from this .venv environment to user's PATH. Note that user
   does not have admin access to the computer. Move this PATH variable to
   the top of the list so that when the script look for python, it finds this
   first installed of other python system may have pre-installed.
6. Check if xlwings add in is installed. If not, install this by `xlwigs
addin install`
7. Copy over 'PERSONAL.XLSB' file from @tools folder to user's XLSTART
   folder. If the file already exists, override this. If excel is already
   running, request user's permission to kill the excel so that the file can
   be copied over successfully.

Let us make a plan first to implement this feature.
