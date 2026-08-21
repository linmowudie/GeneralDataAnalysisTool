# API Tests

This directory contains PowerShell scripts for testing the Data Analysis Tool API endpoints.

## Test Files

- `test_health_check.ps1` - Tests health check and root endpoints
- `test_data_import.ps1` - Tests data import endpoints
- `test_data_preview.ps1` - Tests data preview endpoints
- `test_data_cleaning.ps1` - Tests data cleaning endpoints
- `test_data_analysis.ps1` - Tests data analysis endpoints
- `test_data_visualization.ps1` - Tests data visualization endpoints
- `test_cleanup_task.ps1` - Tests cleanup task endpoints
- `run_all_tests.ps1` - Runs all test scripts sequentially

## Prerequisites

1. The API server must be running on `http://localhost:8000`
2. PowerShell 5.1 or later

## Running Tests

To run all tests:

```powershell
.\run_all_tests.ps1
```

To run a specific test:

```powershell
.\test_health_check.ps1
```

## Notes

- Tests create and destroy sessions as needed
- Tests are designed to be run against a fresh API instance
- Some tests may fail if the API is not properly configured or if required dependencies are missing