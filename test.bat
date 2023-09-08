@echo off
setlocal enabledelayedexpansion

rem Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python is already installed.
) else (
    echo Installing Python...
    rem You can replace the URL with the latest Python download link.
    curl -o python-3.11.5-amd64.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
    start /wait python-3.11.5-amd64.exe /quiet
    del python-3.11.5-amd64.exe
)

rem Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% == 0 (
    echo pip is already installed.
) else (
    echo Installing pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
)

rem Install requests and PyQt6
echo Installing requests and PyQt6...
pip install requests
pip install PyQt6

echo Installation complete.
exit /b 0
