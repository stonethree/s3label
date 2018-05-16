Write-Host "Installing npm requirements"
& cd frontend\spa
& npm install
if ($LastExitCode -gt 0) {
    Exit $LastExitCode
}