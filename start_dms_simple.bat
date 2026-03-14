@echo off
title Truck DMS - Simple Launcher
color 0A

echo ========================================
echo      Truck DMS - Simple Launcher
echo ========================================
echo.

:: Set working directory
cd /d "%~dp0"

:: Find Python 3.11
echo [1/4] Finding Python 3.11...

set "PYTHON_CMD="
for %%P in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Python311\python.exe"
    "C:\Program Files\Python311\python.exe"
) do (
    if exist %%P (
        set "PYTHON_CMD=%%~P"
        echo Found Python: %%P
        goto :python_found
    )
)

:: Try generic python
python --version 2>&1 | find "3.11" >nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    echo Found Python 3.11 in PATH
    goto :python_found
)

echo ERROR: Python 3.11 not found!
echo Please install Python 3.11 from https://www.python.org/
pause
exit /b 1

:python_found
echo.

:: Create virtual environment
echo [2/4] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists
)

:: Activate and install packages
echo [3/4] Installing packages...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

pip install flask pandas openpyxl xlrd xlsxwriter
echo.

:: Create directories
echo [4/4] Setting up directories...
if not exist "uploads" mkdir uploads
if not exist "data" mkdir data
if not exist "config" mkdir config
if not exist "templates" mkdir templates
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js

:: Create config file if needed
if not exist "config\config.py" (
    echo Creating config file...
    copy nul config\config.py
)

echo.
echo ========================================
echo      Starting Truck DMS
echo ========================================
echo.
echo Opening browser...
start http://localhost:5000

echo Starting server at http://localhost:5000
echo Press CTRL+C to stop
echo.

python app.py

pause
