# PowerShell script to compile Python app to Windows .exe and execute it
# 1. Install PyInstaller if not present
# 2. Run PyInstaller to bundle all data (images, audio, config, etc.)
# 3. Execute the resulting .exe

# Application metadata
$appName = 'AutoAcceptApp'
$appVersionFile = Join-Path $PSScriptRoot 'version.txt'

# Update version from version.txt if present
if (Test-Path $appVersionFile) {
    $appVersion = Get-Content $appVersionFile | Select-Object -First 1
    # Auto-increment patch version
    if ($appVersion -match '^(\\d+)\\.(\\d+)\\.(\\d+)$') {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        $patch = [int]$Matches[3] + 1
        $newVersion = "$major.$minor.$patch"
        Set-Content $appVersionFile $newVersion
        $appVersion = $newVersion
        Write-Host "Auto-incremented version to $appVersion"
    }
} else {
    $appVersion = '3.0.0'
    Set-Content $appVersionFile $appVersion
}

Write-Host "Starting $appName version $appVersion"

# Set variables
$projectRoot = "$PSScriptRoot"
$srcDir = Join-Path $projectRoot 'src'
$mainPy = Join-Path $srcDir 'main.py'
$distDir = Join-Path $projectRoot 'dist'
$exeName = 'main.exe'

# Step 1: Ensure PyInstaller is installed
if (-not (pip show pyinstaller)) {
    Write-Host 'Installing PyInstaller...'
    pip install pyinstaller
}

# Step 2: Build the .exe with all data included
# Collect all files in src/bin and config files
$binDir = Join-Path $srcDir 'bin'
$binFiles = Get-ChildItem -Path $binDir -File | ForEach-Object { "--add-data=$($binDir)\$($_.Name);bin" }
$configFiles = @("--add-data=$srcDir\\config.json;.")
$datas = $binFiles + $configFiles

# Remove previous build
if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }
if (Test-Path (Join-Path $srcDir 'build')) { Remove-Item (Join-Path $srcDir 'build') -Recurse -Force }
if (Test-Path (Join-Path $srcDir 'main.spec')) { Remove-Item (Join-Path $srcDir 'main.spec') -Force }

# Build the argument list for PyInstaller
$pyinstallerArgs = @('--onefile', '--noconsole', "--icon=$binDir\\icon.ico") + $datas + $mainPy
Write-Host "Running: pyinstaller $($pyinstallerArgs -join ' ')"
Push-Location $projectRoot
pyinstaller @pyinstallerArgs
Pop-Location

# Step 3: Execute the .exe
$exePath = Join-Path $distDir $exeName
$targetDir = 'C:\Users\CleudeirSilva\My Drive\auto_accept'
$versionedExeName = "auto-accept-$appVersion.exe"
$versionedTargetPath = Join-Path $targetDir $versionedExeName
$targetPath = Join-Path $targetDir 'main.exe'

if (Test-Path $exePath) {
    Write-Host "Moving $exePath to $versionedTargetPath..."
    Move-Item -Path $exePath -Destination $versionedTargetPath -Force
    Write-Host "Copying $versionedTargetPath to $targetPath..."
    Copy-Item -Path $versionedTargetPath -Destination $targetPath -Force
    Write-Host "Running $targetPath..."
    Start-Process $targetPath
} else {
    Write-Host "Executable not found: $exePath"
}
