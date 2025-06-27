# PowerShell script to compile Python app to Windows .exe and execute it
# 1. Install PyInstaller if not present
# 2. Run PyInstaller to bundle all data (images, audio, config, etc.)
# 3. Execute the resulting .exe

# Set variables
$projectRoot = "$PSScriptRoot"
$srcDir = Join-Path $projectRoot 'src'
$mainPy = Join-Path $srcDir 'main.py'
$distDir = Join-Path $srcDir 'dist'
$exeName = 'main.exe'

# Step 1: Ensure PyInstaller is installed
if (-not (pip show pyinstaller)) {
    Write-Host 'Installing PyInstaller...'
    pip install pyinstaller
}

# Step 2: Build the .exe with all data included
# Collect all files in src/bin and config files
$binDir = Join-Path $srcDir 'bin'
$binFiles = Get-ChildItem -Path $binDir -File | ForEach-Object { "--add-data=src\\bin\\$($_.Name);bin" }
$configFiles = @('--add-data=config.json;.')
$datas = $binFiles + $configFiles

# Remove previous build
if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }
if (Test-Path (Join-Path $srcDir 'build')) { Remove-Item (Join-Path $srcDir 'build') -Recurse -Force }
if (Test-Path (Join-Path $srcDir 'main.spec')) { Remove-Item (Join-Path $srcDir 'main.spec') -Force }

# Build the argument list for PyInstaller
$pyinstallerArgs = @('--onefile', '--noconsole', "--icon=src/bin/icon.ico") + $datas + $mainPy
Write-Host "Running: pyinstaller $($pyinstallerArgs -join ' ')"
pyinstaller @pyinstallerArgs

# Step 3: Execute the .exe
$exePath = Join-Path $projectRoot 'dist/main.exe'
if (Test-Path $exePath) {
    Write-Host "Running $exePath..."
    Start-Process $exePath
} else {
    Write-Host "Executable not found: $exePath"
}
