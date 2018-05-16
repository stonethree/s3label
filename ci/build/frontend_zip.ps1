Write-Host "Running 'npm build' script"

& cd frontend\spa
& npm run-script build
if ($LastExitCode -gt 0) {
  exit $LastExitCode
}

& cd ..\..\
Write-Host "Compiling deployment zip file for frontend"
& 7z a -t7z "frontend.7z" "frontend\spa\dist"
if ($LastExitCode -gt 0) {
  exit $LastExitCode
}


