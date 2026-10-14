#Requires -Version 7.0
param([switch]$SkipBuild, [switch]$SkipIndex)

$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
Push-Location $projectPath
try {
    if (-not (Test-Path -LiteralPath '.env')) {
        $passwordBytes = New-Object byte[] 24
        [Security.Cryptography.RandomNumberGenerator]::Fill($passwordBytes)
        $adminPassword = 'Dof!' + [Convert]::ToBase64String($passwordBytes)
        $configuration = (Get-Content '.env.example' -Raw).Replace('ADMIN_PASSWORD=', "ADMIN_PASSWORD=$adminPassword")
        [IO.File]::WriteAllText((Join-Path $projectPath '.env'), $configuration)
        Write-Output 'Created local .env with a randomly generated administrator password.'
    }
    $settings = @{}
    foreach ($line in Get-Content '.env') {
        if ($line -match '^([A-Z_]+)=(.*)$') { $settings[$matches[1]] = $matches[2] }
    }
    if (-not $settings.ADMIN_PASSWORD) { throw 'Set ADMIN_PASSWORD in .env before starting.' }

    docker info --format '{{.ServerVersion}}'
    if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop and wait for its engine, then run this script again.' }
    foreach ($model in @($settings.OLLAMA_MODEL, $settings.EMBEDDING_MODEL)) {
        ollama show $model *> $null
        if ($LASTEXITCODE -ne 0) {
            ollama pull $model
            if ($LASTEXITCODE -ne 0) { throw "Could not download model $model" }
        }
    }
    if ($SkipBuild) { docker compose up -d --wait --wait-timeout 120 }
    else { docker compose up -d --build --wait --wait-timeout 120 }
    if ($LASTEXITCODE -ne 0) { throw 'Services could not start. Check docker compose logs.' }
    if (-not $SkipIndex) {
        docker compose exec -T backend python -m capidofchat_api.local_rag
        if ($LASTEXITCODE -ne 0) { throw 'Document indexing failed. Check that Ollama and both models are available.' }
    }
    Write-Output "Application: http://localhost:$($settings.FRONTEND_PORT)"
    Write-Output "Local recovery mailbox: http://localhost:$($settings.MAIL_PORT)"
    Write-Output "Administrator: $($settings.ADMIN_EMAIL). Password is stored in .env."
} finally {
    Pop-Location
}
