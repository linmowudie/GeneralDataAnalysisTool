# Test Data Import API
# 测试数据导入API

# 设置基本URL
$baseUrl = "http://127.0.0.1:8000/api/import"
$session_id = ""

# 创建会话
Write-Host "Creating session..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/create-session" -Method POST
    $content = $response.Content | ConvertFrom-Json
    $session_id = $content.session_id
    Write-Host "Session created: $session_id" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to create session: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 测试步骤状态
Write-Host "Checking step status..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/step-status?session_id=$session_id" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Step status: $($content.status | ConvertTo-Json -Depth 10)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get step status: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试重置步骤
Write-Host "Testing step reset..." -ForegroundColor Green
try {
    $body = @{
        session_id = $session_id
        step = "import"
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/reset-step" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Reset step result: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to reset step: $($_.Exception.Message)" -ForegroundColor Red
}

# 结束会话
Write-Host "Ending session..." -ForegroundColor Green
try {
    $body = @{
        session_id = $session_id
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/end-session" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Session ended: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to end session: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Data import API tests completed." -ForegroundColor Green