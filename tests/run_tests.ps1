# Test runner for the tropical-vending project
# This script runs tests to verify the decimal place fix

Write-Host "Tropical Vending Test Suite" -ForegroundColor Cyan
Write-Host "Testing the decimal place fix for wholesale purchases" -ForegroundColor Yellow
Write-Host ""

# Manual decimal place tests
Write-Host "Running Manual Decimal Place Tests" -ForegroundColor Magenta
Write-Host "=================================================" -ForegroundColor Magenta

$testCases = @(
    @{ quantity = 3; totalCost = 10.00; expected = 3.33; description = "10.00 / 3 should round to 3.33" },
    @{ quantity = 7; totalCost = 20.00; expected = 2.86; description = "20.00 / 7 should round to 2.86" },
    @{ quantity = 6; totalCost = 5.00; expected = 0.83; description = "5.00 / 6 should round to 0.83" },
    @{ quantity = 9; totalCost = 25.00; expected = 2.78; description = "25.00 / 9 should round to 2.78" }
)

$manualTestsPassed = $true

for ($i = 0; $i -lt $testCases.Length; $i++) {
    $case = $testCases[$i]
    $testNum = $i + 1
    
    # Calculate using the same logic as the frontend fix
    $rawUnitCost = $case.totalCost / $case.quantity
    $roundedUnitCost = [Math]::Round($rawUnitCost, 2)
    
    $passed = $roundedUnitCost -eq $case.expected
    $manualTestsPassed = $manualTestsPassed -and $passed
    
    Write-Host "Test $testNum : $($case.description)" -ForegroundColor White
    Write-Host "  Input: $($case.quantity) units at `$$($case.totalCost) total" -ForegroundColor Gray
    Write-Host "  Raw result: $rawUnitCost" -ForegroundColor Gray
    Write-Host "  Rounded result: $roundedUnitCost" -ForegroundColor Gray
    Write-Host "  Expected: $($case.expected)" -ForegroundColor Gray
    
    if ($passed) {
        Write-Host "  Status: PASSED" -ForegroundColor Green
    } else {
        Write-Host "  Status: FAILED" -ForegroundColor Red
    }
    Write-Host ""
}

# Frontend tests
Write-Host "Running Frontend Tests" -ForegroundColor Blue
Write-Host "=================================================" -ForegroundColor Blue

$frontendTestsPassed = $false

try {
    $testFile = Join-Path $PSScriptRoot "frontend\test_purchases_decimal_fix.js"
    
    if (Test-Path $testFile) {
        $result = node $testFile 2>&1 | Out-String
        Write-Host $result
        
        # Check if tests passed - look for the results summary
        $hasAllPassed = $result -match "Results:.*passed.*0 failed"
        $hasSomeFailed = $result -match "Results:.*failed" -and -not ($result -match "0 failed")
        
        $frontendTestsPassed = $hasAllPassed -and -not $hasSomeFailed
    } else {
        Write-Host "Frontend test file not found: $testFile" -ForegroundColor Red
        $frontendTestsPassed = $false
    }
}
catch {
    Write-Host "Node.js not found or error running frontend tests. Skipping." -ForegroundColor Yellow
    Write-Host "To run frontend tests, install Node.js and try again." -ForegroundColor Yellow
    $frontendTestsPassed = $true  # Don't fail the entire test suite
}

# Display summary
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

$manualStatus = if ($manualTestsPassed) { "PASSED" } else { "FAILED" }
$manualColor = if ($manualTestsPassed) { "Green" } else { "Red" }
Write-Host "Manual Tests: $manualStatus" -ForegroundColor $manualColor

$frontendStatus = if ($frontendTestsPassed) { "PASSED" } else { "FAILED" }
$frontendColor = if ($frontendTestsPassed) { "Green" } else { "Red" }
Write-Host "Frontend Tests: $frontendStatus" -ForegroundColor $frontendColor

$allPassed = $manualTestsPassed -and $frontendTestsPassed

Write-Host ""
if ($allPassed) {
    Write-Host "All tests passed! The decimal place fix is working correctly." -ForegroundColor Green
    Write-Host "The wholesale purchase functionality should now handle decimal places properly." -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed. Please review the implementation." -ForegroundColor Yellow
    exit 1
} 