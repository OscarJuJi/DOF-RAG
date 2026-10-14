#Requires -Version 7.0
param(
    [string]$StartDate = '2024-01-01',
    [string]$EndDate = '',
    [switch]$Refresh
)

$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
if (-not $EndDate) { $EndDate = [DateTime]::UtcNow.AddHours(-6).ToString('yyyy-MM-dd') }
Push-Location $projectPath
try {
    docker compose build dof-mcp
    if ($LASTEXITCODE -ne 0) { throw 'Could not build the DOF connector.' }
    docker compose up -d --no-deps dof-mcp
    if ($LASTEXITCODE -ne 0) { throw 'Could not start the DOF MCP.' }
    $syncArguments = @('compose', 'run', '--rm', '--no-deps', 'dof-mcp', 'python', '-m', 'dof_mcp.sync', '--start', $StartDate, '--end', $EndDate)
    if ($Refresh) { $syncArguments += '--refresh' }
    & docker @syncArguments
    if ($LASTEXITCODE -ne 0) { throw 'Archive incomplete. Inspect data/dof/status.json and rerun to retry.' }
    docker compose run --rm --no-deps dof-mcp python -m dof_mcp.audit --start $StartDate --end $EndDate
    if ($LASTEXITCODE -ne 0) { throw 'Archive verification failed. Inspect data/dof/audit.json.' }
} finally {
    Pop-Location
}
