# Test Cleanup Task API
# 测试清理任务API

# 设置基本URL
$baseUrl = "http://127.0.0.1:8000/api/cleanup"

# 测试清理任务状态
Write-Host "Testing cleanup task status..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/status" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Cleanup task status: $($content.status)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get cleanup task status: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试获取清理统计信息
Write-Host "Testing cleanup stats..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/stats" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Cleanup stats:" -ForegroundColor Yellow
    Write-Host "Files removed: $($content.files_removed)" -ForegroundColor Yellow
    Write-Host "Space freed: $($content.space_freed)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get cleanup stats: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试运行清理任务
Write-Host "Testing run cleanup..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/run" -Method POST
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Cleanup result: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to run cleanup: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试运行步骤清理任务
Write-Host "Testing run step cleanup..." -ForegroundColor Green
try {
    $body = @{
        step = "import"
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/run-step" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Step cleanup result: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to run step cleanup: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Cleanup task API tests completed." -ForegroundColor Green