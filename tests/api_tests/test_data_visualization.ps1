# Test Data Visualization API
# 测试数据可视化API

# 设置基本URL
$baseUrl = "http://127.0.0.1:8000/api/visualization"

# 先创建一个会话用于测试
Write-Host "Creating session for visualization tests..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/import/create-session" -Method POST
    $content = $response.Content | ConvertFrom-Json
    $session_id = $content.session_id
    Write-Host "Session created: $session_id" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to create session: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 测试获取可用图表类型
Write-Host "Testing available chart types..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/available-charts" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Available chart types: $($content.chart_types -join ', ')" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get available chart types: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试生成图表
Write-Host "Testing generate chart..." -ForegroundColor Green
try {
    $body = @{
        session_id = $session_id
        chart_type = "scatter"
        parameters = "{}"
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/generate-chart" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Chart generation result: $($content.status)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to generate chart: $($_.Exception.Message)" -ForegroundColor Red
}

# 清理会话
Write-Host "Ending session..." -ForegroundColor Green
try {
    $body = @{
        session_id = $session_id
    }
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/import/end-session" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Session ended: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to end session: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Data visualization API tests completed." -ForegroundColor Green