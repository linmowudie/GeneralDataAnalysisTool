# Run All API Tests
# 运行所有API测试

Write-Host "Starting all API tests..." -ForegroundColor Cyan

# 定义测试文件列表
$testFiles = @(
    "test_health_check.ps1",
    "test_data_import.ps1",
    "test_data_preview.ps1",
    "test_data_cleaning.ps1",
    "test_data_analysis.ps1",
    "test_data_visualization.ps1",
    "test_cleanup_task.ps1"
)

# 运行每个测试文件
foreach ($testFile in $testFiles) {
    Write-Host "`n========================================" -ForegroundColor Magenta
    Write-Host "Running $testFile..." -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    
    try {
        & ".\$testFile"
        Write-Host "$($testFile) completed successfully." -ForegroundColor Green
    } catch {
        Write-Host "Failed to run $($testFile): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "All API tests completed." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan