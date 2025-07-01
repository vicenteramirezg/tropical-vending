# Test Suite for Tropical Vending Project

This test suite verifies that the decimal place fix for wholesale purchases is working correctly across both frontend and backend components.

## Problem Addressed

The original issue was that when adding wholesale purchases, the frontend would calculate `cost_per_unit` by dividing `total_cost` by `quantity`, which could result in values with more than 2 decimal places (e.g., `1.333333...`). However, the backend's `WholesalePurchaseSerializer` has a `cost_per_unit` field with validation that requires exactly 2 decimal places:

```python
cost_per_unit = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
```

This caused validation errors like:
```
cost_per_unit: ["Ensure that there are no more than 2 decimal places."]
```

## Solution Implemented

The fix involved rounding the `cost_per_unit` to exactly 2 decimal places in two places in the frontend:

1. **In `calculateUnitCost` function**: 
   ```javascript
   purchaseForm.value.cost_per_unit = Math.round((totalCost / quantity) * 100) / 100;
   ```

2. **In `savePurchase` function**:
   ```javascript
   cost_per_unit: Math.round(unitCost.value * 100) / 100
   ```

## Test Structure

```
tests/
├── README.md                           # This file
├── run_tests.ps1                      # PowerShell test runner
├── run_tests.py                       # Python test runner
├── backend/
│   └── test_wholesale_purchase.py     # Django backend tests
└── frontend/
    └── test_purchases_decimal_fix.js   # JavaScript frontend tests
```

## Running Tests

### Option 1: PowerShell (Recommended for Windows)
```powershell
.\tests\run_tests.ps1
```

### Option 2: Python
```bash
python tests/run_tests.py
```

### Option 3: Individual Test Files

**Frontend Tests:**
```bash
node tests/frontend/test_purchases_decimal_fix.js
```

**Backend Tests:**
```bash
cd backend
python ../tests/backend/test_wholesale_purchase.py
```

## Test Categories

### 1. Manual Decimal Place Tests
These tests verify the core mathematical rounding logic using the same calculations as the frontend fix:

- `10.00 / 3 = 3.333...` → should round to `3.33`
- `20.00 / 7 = 2.857142...` → should round to `2.86`
- `5.00 / 6 = 0.833...` → should round to `0.83`
- `25.00 / 9 = 2.777...` → should round to `2.78`

### 2. Frontend Tests
Tests the JavaScript functions that handle decimal place rounding:

- `calculateUnitCost()` function
- Rounding logic used in `savePurchase()`
- Edge cases with repeating decimals

### 3. Backend Tests
Django tests that verify:

- `WholesalePurchaseSerializer` accepts properly rounded values
- `WholesalePurchaseSerializer` rejects values with too many decimal places
- Model calculations work correctly
- API endpoints handle decimal validation properly

## Test Cases Covered

| Quantity | Total Cost | Expected Unit Cost | Description |
|----------|------------|-------------------|-------------|
| 3 | $10.00 | $3.33 | Repeating decimal (3.333...) |
| 7 | $20.00 | $2.86 | Long decimal (2.857142...) |
| 4 | $8.00 | $2.00 | Exact division |
| 6 | $5.00 | $0.83 | Small repeating decimal |
| 9 | $25.00 | $2.78 | Another repeating decimal |

## Expected Output

When all tests pass, you should see:

```
🎉 All tests passed! The decimal place fix is working correctly.
The wholesale purchase functionality should now handle decimal places properly.
```

## Dependencies

- **Python 3.x** with Django (for backend tests)
- **Node.js** (for frontend tests, optional)
- **PowerShell** (for the PowerShell test runner)

## Troubleshooting

### Node.js Not Found
If you see "Node.js not found", the frontend tests will be skipped. This is not critical as the manual tests cover the same logic.

### Django Import Errors
Make sure you're in the correct directory and that Django is installed:
```bash
cd backend
pip install -r ../requirements.txt
```

### Permission Errors
On Windows, you may need to set the execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Adding New Tests

To add new test cases:

1. **For decimal calculations**: Add to the `testCases` array in the respective test files
2. **For backend functionality**: Add to `tests/backend/test_wholesale_purchase.py`
3. **For frontend functionality**: Add to `tests/frontend/test_purchases_decimal_fix.js`

## Integration with CI/CD

These tests can be integrated into continuous integration pipelines:

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    python tests/run_tests.py
```

Or for PowerShell environments:
```yaml
- name: Run Tests
  run: |
    .\tests\run_tests.ps1
``` 