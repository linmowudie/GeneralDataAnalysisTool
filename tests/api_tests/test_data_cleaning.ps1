# Test Data Cleaning API
# 测试数据清洗API

# 设置基本URL
$baseUrl = "http://127.0.0.1:8000/api/cleaning"

# 先创建一个会话用于测试
Write-Host "Creating session for cleaning tests..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/import/create-session" -Method POST
    $content = $response.Content | ConvertFrom-Json
    $session_id = $content.session_id
    Write-Host "Session created: $session_id" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to create session: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 测试获取清洗模式
Write-Host "Testing cleaning modes..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/cleaning-modes" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Available cleaning modes: $($content.modes -join ', ')" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get cleaning modes: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试数据清洗
Write-Host "Testing data cleaning..." -ForegroundColor Green
try {
    $body = @{
        session_id = $session_id
        mode = "standard"
        is_custom = $false
        parameters = "{}"
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/clean-data" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Cleaning result: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to clean data: $($_.Exception.Message)" -ForegroundColor Red
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

Write-Host "Data cleaning API tests completed." -ForegroundColor Green