# Project startup script
# Supports starting frontend, backend or all services

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("frontend", "backend", "all")]
    [string]$mode = "all"
)

Write-Host "Starting data analysis tool project..." -ForegroundColor Green

switch ($mode) {
    "frontend" {
        Write-Host "Starting frontend service..." -ForegroundColor Yellow
        Set-Location -Path "$PSScriptRoot\frontend\dashboard"
        npm run dev
    }
    "backend" {
        Write-Host "Starting backend API service..." -ForegroundColor Yellow
        Set-Location -Path $PSScriptRoot
        python run_api.py
    }
    "all" {
        Write-Host "Starting all frontend and backend services..." -ForegroundColor Yellow
        
        # Start backend service
        Write-Host "Starting backend API service on http://127.0.0.1:8000" -ForegroundColor Cyan
        Start-Process -FilePath "python" -ArgumentList "run_api.py" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
        
        # Wait a few seconds for backend to start
        Write-Host "Waiting for backend to start..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
        
        # Start frontend service
        Write-Host "Starting frontend dashboard service on http://localhost:5173" -ForegroundColor Cyan
        Set-Location -Path "$PSScriptRoot\frontend\dashboard"
        npm run dev
    }
}

Write-Host "Project startup completed!" -ForegroundColor Green