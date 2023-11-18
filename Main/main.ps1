# Define the desired Python version
$pythonVersion = "3.10.0"

# Check if Python 3.10.0 is already installed
$pythonInstalled = "C:\Program Files\Python310"

if (-not (Test-Path $pythonInstalled)) {
	Clear
    # Python 3.10.0 is not installed, proceed with installation
    Write-Host "Python $pythonVersion is not installed. Installing now..." -ForegroundColor White

    # Define the download URL for Python 3.10.0
    $pythonInstallerUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"

    try {
        # Download Python installer
        Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile "python-$pythonVersion-amd64.exe"

        # Install Python 3.10.0
        Start-Process -Wait -FilePath ".\python-$pythonVersion-amd64.exe" -ArgumentList "/passive", "InstallAllUsers=1", "PrependPath=1"

        # Check if the installation was successful
        $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonInstalled -eq $null) {
            throw "Error: Python $pythonVersion installation failed."
        } else {
			Clear
            Write-Host "Python $pythonVersion has been successfully installed." -ForegroundColor Green
        }
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
		Start-Sleep -Seconds 10
        exit 1
    } finally {
        # Remove the installation executable
        Remove-Item -Path ".\python-$pythonVersion-amd64.exe" -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "Python $pythonVersion is already installed." -ForegroundColor Green
	Sleep -Seconds 1
}

# Add Python to the system environment variables (PATH)
$pythonPath = (Get-Command python).Path
if ($env:Path -notlike "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\") {
    try {
		$newPath = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\"
        [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$newPath", [System.EnvironmentVariableTarget]::User)
        Write-Host "Python path has been added to the system environment variables."-ForegroundColor Green
    } catch {
        Write-Host "Error adding Python path to the system environment variables" -ForegroundColor Red
		Start-Sleep -Seconds 5
        exit 1
    }
} else {
    Write-Host "Python path is already in the system environment variables." ????????????
}

# Inform the user about the completion of the script
Write-Host "Python 3.10.0 installation and environment setup completed successfully." -ForegroundColor Green
Sleep -Seconds 1
# Display a message if Python 3.10.0 installation is canceled
if (-not (Test-Path $pythonInstalled)) {
	Clear
    Write-Host "Python 3.10.0 installation was canceled.(Installation could not run with administrator rights.)" -ForegroundColor Red
	Sleep -Seconds 15
	exit 1
}


# Check if Git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    # If Git is not installed, install it using winget
    Write-Host 'Installing Git using winget...'
    winget install Git -e
    
    # Check if installation was successful
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host 'Git has been successfully installed.' -ForegroundColor Green
		Start-Sleep -Seconds 5
    } else {
        Write-Host 'Failed to install Git. Please check the installation.' -ForegroundColor Red
		Start-Sleep -Seconds 10
    }
} else {
    Write-Host 'Git is already installed.' -ForegroundColor Green
	Start-Sleep -Seconds 5
}


