# Test Data Analysis API
# 测试数据分析API

# 设置基本URL
$baseUrl = "http://127.0.0.1:8000/api/analysis"

# 先创建一个会话用于测试
Write-Host "Creating session for analysis tests..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/session/create" -Method POST
    $content = $response.Content | ConvertFrom-Json
    $session_id = $content.session_id
    Write-Host "Session created: $session_id" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to create session: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 测试获取可用模型
Write-Host "Testing available models..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/available-models" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Available models: $($content.models -join ', ')" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get available models: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试运行分析
Write-Host "Testing run analysis..." -ForegroundColor Green
try {
    $body = @{
        session_id = $session_id
        model_type = "linear_regression"
        parameters = "{}"
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/run-analysis" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Analysis result: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to run analysis: $($_.Exception.Message)" -ForegroundColor Red
}

# 清理会话
Write-Host "Ending session..." -ForegroundColor Green
try {
    $body = @{
        session_id = $session_id
    }
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/session/end" -Method POST -Body $body
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Session ended: $($content.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to end session: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Data analysis API tests completed." -ForegroundColor Green