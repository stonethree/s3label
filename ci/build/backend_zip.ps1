& 7z a -t7z "backend.7z" backend/
if ($LastExitCode -gt 0) {
    Exit $LastExitCode
}