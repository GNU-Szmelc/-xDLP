# Define the URL of the Python installer
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"

# Define the path where you want to save the installer
$installerPath = "$env:USERPROFILE\Downloads\python-3.11.5-amd64.exe"

# Download the Python installer
Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath

# Start the Python installer with silent options
Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait

# Clean up the installer file
Remove-Item $installerPath

# Verify Python installation
$pythonVersion = (Get-Command python).FileVersionInfo.ProductVersion
Write-Host "Python $pythonVersion has been installed."
