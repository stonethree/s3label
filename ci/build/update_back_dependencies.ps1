Write-Host "Creating virtual environment"

& 'C:\Program Files\Python35\Scripts\virtualenv' venv
if ($LastExitCode -gt 0) {
    Exit $LastExitCode
}

Get-ChildItem -Filter '*.pyc' -Force -Recurse | Remove-Item -Force

Remove-Item C:\Users\Administrator\AppData\Local\Temp\* -Force -Recurse

Write-Host "Installing pip requirements"

& venv\Scripts\pip.exe install -r backend\requirements.txt
if ($LastExitCode -gt 0) {
    Exit $LastExitCode
}