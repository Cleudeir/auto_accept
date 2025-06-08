$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Dota 2 Auto Accept.lnk")
$Shortcut.TargetPath = "C:\Users\CleudeirSilva\Documents\Pessoal\auto_accept\launcher.vbs"
$Shortcut.WorkingDirectory = "C:\Users\CleudeirSilva\Documents\Pessoal\auto_accept"
# Set icon if available
if (Test-Path "C:\Users\CleudeirSilva\Documents\Pessoal\auto_accept\icon.ico") {
    $Shortcut.IconLocation = "C:\Users\CleudeirSilva\Documents\Pessoal\auto_accept\icon.ico"
}
$Shortcut.Save()
Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
