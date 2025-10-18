# Check API Status
# 检查API状态

Write-Host "Checking if API server is running..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -Method GET
    if ($response.StatusCode -eq 200) {
        $content = $response.Content | ConvertFrom-Json
        Write-Host "API Server Status: $($content.status)" -ForegroundColor Green
        Write-Host "Message: $($content.message)" -ForegroundColor Yellow
        Write-Host "API server is running and accessible." -ForegroundColor Green
    } else {
        Write-Host "API server returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "Failed to connect to API server." -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please make sure the API server is running on http://127.0.0.1:8000" -ForegroundColor Yellow
}