@echo off
setlocal

:: Define the URL of the Python installer
set "pythonInstallerUrl=https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"

:: Define the path where you want to save the installer
set "installerPath=%USERPROFILE%\Downloads\python-3.11.5-amd64.exe"

:: Download the Python installer
powershell -command "(New-Object System.Net.WebClient).DownloadFile('%pythonInstallerUrl%', '%installerPath%')"

:: Start the Python installer with silent options
"%installerPath%" /quiet InstallAllUsers=1 PrependPath=1

:: Clean up the installer file
del "%installerPath%"

:: Verify Python installation
python --version

endlocal
