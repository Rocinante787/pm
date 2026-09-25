$ErrorActionPreference = "Stop"
$rootDir = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $rootDir

if (-not (Test-Path "$rootDir\data")) {
    New-Item -ItemType Directory -Path "$rootDir\data" | Out-Null
}

$hasDocker = Get-Command docker -ErrorAction SilentlyContinue

if ($hasDocker) {
    Write-Host "Building Docker image pm-app..."
    docker build -t pm-app .

    Write-Host "Stopping existing pm-app container..."
    docker rm -f pm-app 2>$null | Out-Null

    $envArgs = @()
    if (Test-Path "$rootDir\.env") {
        $envArgs += "--env-file"
        $envArgs += "$rootDir\.env"
    }

    Write-Host "Starting pm-app container on port 8000..."
    docker run -d --name pm-app -p 8000:8000 -v "${rootDir}/data:/app/data" @envArgs pm-app
    Write-Host "App is running at http://localhost:8000"
} else {
    Write-Host "Docker not detected in PATH. Starting locally with uv..."
    Set-Location "$rootDir\backend"
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
}

