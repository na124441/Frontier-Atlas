@echo off
setlocal
set VENV_DIR=C:\Users\nayan\.venv_scraper
set VENV_PY=%VENV_DIR%\Scripts\python.exe
set UV_PY=C:\Users\nayan\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe

if exist "%VENV_PY%" (
    "%VENV_PY%" cli.py %*
    if %ERRORLEVEL% equ 0 goto :eof
)

if exist "%UV_PY%" (
    set "VIRTUAL_ENV=%VENV_DIR%"
    set "PYTHONPATH=%~dp0src;%VENV_DIR%\Lib\site-packages"
    "%UV_PY%" cli.py %*
    goto :eof
)

echo Error: Python interpreter not found.
pause
exit /b 1
