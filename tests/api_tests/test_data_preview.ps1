# Test Data Preview API
# 测试数据预览API

# 设置基本URL
$baseUrl = "http://127.0.0.1:8000/api/preview"

# 先创建一个会话用于测试
Write-Host "Creating session for preview tests..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/import/create-session" -Method POST
    $content = $response.Content | ConvertFrom-Json
    $session_id = $content.session_id
    Write-Host "Session created: $session_id" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to create session: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 测试数据预览
Write-Host "Testing data preview..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/data-preview?session_id=$session_id" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Data preview result:" -ForegroundColor Yellow
    Write-Host "File name: $($content.file_name)" -ForegroundColor Yellow
    Write-Host "Total rows: $($content.total_rows)" -ForegroundColor Yellow
    Write-Host "Total columns: $($content.total_columns)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get data preview: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试数据集信息
Write-Host "Testing dataset info..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/dataset-info?session_id=$session_id" -Method GET
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Dataset info result:" -ForegroundColor Yellow
    Write-Host "Dataset name: $($content.dataset_name)" -ForegroundColor Yellow
    Write-Host "Total records: $($content.total_records)" -ForegroundColor Yellow
    Write-Host "Features count: $($content.features_count)" -ForegroundColor Yellow
} catch {
    Write-Host "Failed to get dataset info: $($_.Exception.Message)" -ForegroundColor Red
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

Write-Host "Data preview API tests completed." -ForegroundColor Green