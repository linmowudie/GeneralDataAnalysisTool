# Test Health Check and Root API
# 测试健康检查和根API

# 设置基本URL
$baseUrl = "http://127.0.0.1:8000/api"

# 测试健康检查
Write-Host "Testing health check..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Health check result:" -ForegroundColor Yellow
    Write-Host "Status: $($content.status)" -ForegroundColor Yellow
    Write-Host "Message: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to perform health check: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试根路径
Write-Host "Testing root path..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Root path result:" -ForegroundColor Yellow
    Write-Host "Message: $($content.message)" -ForegroundColor Yellow
    Write-Host "Version: $($content.version)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to access root path: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Health check and root API tests completed." -ForegroundColor Green