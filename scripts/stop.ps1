$ErrorActionPreference = "SilentlyContinue"
$hasDocker = Get-Command docker -ErrorAction SilentlyContinue

if ($hasDocker) {
    Write-Host "Stopping pm-app container..."
    docker stop pm-app | Out-Null
    docker rm pm-app | Out-Null
    Write-Host "pm-app container stopped."
} else {
    Write-Host "Stopping any local uvicorn processes..."
    Get-Process -Name "uvicorn", "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*app.main:app*" } | Stop-Process -Force
    Write-Host "Stopped."
}

