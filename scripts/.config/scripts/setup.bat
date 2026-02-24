@echo off
REM Use Windows system certificate store (needed for corporate proxy/SSL inspection)
set UV_NATIVE_TLS=true
REM Increase HTTP timeout for slow corporate networks with SSL inspection (default is 30s)
set UV_HTTP_TIMEOUT=120
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    REM Refresh PATH from registry so uv is available in this session
    for /f "tokens=*" %%A in ('powershell -c "[Environment]::GetEnvironmentVariable('Path','User')"') do set "PATH=%%A;%PATH%"
) else (
    echo uv is already installed.
)
echo Running bid setup...
uv run --quiet --script "%~dp0bid.py" setup
if %errorlevel% neq 0 (
    echo Retrying without cache (antivirus may be blocking cache writes)...
    uv run --no-cache --quiet --script "%~dp0bid.py" setup
)
if %errorlevel% equ 0 (
    echo Setup complete.
) else (
    echo Setup failed. Please check the errors above.
)
pause
