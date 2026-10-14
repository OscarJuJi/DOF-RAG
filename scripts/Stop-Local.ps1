$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    docker compose stop
    if ($LASTEXITCODE -ne 0) { throw 'Could not stop the local services.' }
} finally {
    Pop-Location
}
