#!/usr/bin/env python3
"""
Verification script to test the decimal place fix in the Django backend
"""

import os
import sys
import django
from decimal import Decimal

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

from core.serializers import WholesalePurchaseSerializer
from core.models import Product

def test_decimal_validation():
    """Test that the serializer properly validates decimal places"""
    print("Testing Decimal Place Validation in WholesalePurchaseSerializer")
    print("=" * 60)
    
    # Create a test product if it doesn't exist
    product, created = Product.objects.get_or_create(
        name="Test Product",
        defaults={
            'product_type': 'Soda',
            'unit_type': 'can',
            'inventory_quantity': 0
        }
    )
    
    if created:
        print(f"Created test product: {product.name}")
    else:
        print(f"Using existing test product: {product.name}")
    
    # Test cases that should PASS (exactly 2 decimal places)
    valid_test_cases = [
        {'cost_per_unit': '3.33', 'description': 'Rounded result from 10.00/3'},
        {'cost_per_unit': '2.86', 'description': 'Rounded result from 20.00/7'},
        {'cost_per_unit': '0.83', 'description': 'Rounded result from 5.00/6'},
        {'cost_per_unit': '1.67', 'description': 'Rounded result from 5.00/3'},
        {'cost_per_unit': '2.00', 'description': 'Exact result'},
        {'cost_per_unit': '0.01', 'description': 'Minimum value'},
        {'cost_per_unit': '999.99', 'description': 'Large value with 2 decimals'},
    ]
    
    # Test cases that should FAIL (more than 2 decimal places)
    invalid_test_cases = [
        {'cost_per_unit': '3.333', 'description': 'Raw result from 10.00/3 (too many decimals)'},
        {'cost_per_unit': '2.857142', 'description': 'Raw result from 20.00/7 (too many decimals)'},
        {'cost_per_unit': '1.6666666', 'description': 'Raw result from 5.00/3 (too many decimals)'},
    ]
    
    print("\n✅ Testing VALID cases (should pass):")
    print("-" * 40)
    
    valid_passed = 0
    for i, case in enumerate(valid_test_cases, 1):
        data = {
            'product': product.id,
            'quantity': 1,
            'cost_per_unit': case['cost_per_unit'],
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'Test Supplier'
        }
        
        serializer = WholesalePurchaseSerializer(data=data)
        is_valid = serializer.is_valid()
        
        print(f"Test {i}: {case['description']}")
        print(f"  cost_per_unit: {case['cost_per_unit']}")
        print(f"  Result: {'PASSED' if is_valid else 'FAILED'}")
        
        if not is_valid:
            print(f"  Errors: {serializer.errors}")
        
        if is_valid:
            valid_passed += 1
        
        print()
    
    print(f"Valid tests passed: {valid_passed}/{len(valid_test_cases)}")
    
    print("\n❌ Testing INVALID cases (should fail):")
    print("-" * 40)
    
    invalid_failed = 0
    for i, case in enumerate(invalid_test_cases, 1):
        data = {
            'product': product.id,
            'quantity': 1,
            'cost_per_unit': case['cost_per_unit'],
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'Test Supplier'
        }
        
        serializer = WholesalePurchaseSerializer(data=data)
        is_valid = serializer.is_valid()
        
        print(f"Test {i}: {case['description']}")
        print(f"  cost_per_unit: {case['cost_per_unit']}")
        print(f"  Result: {'FAILED (as expected)' if not is_valid else 'PASSED (unexpected!)'}")
        
        if not is_valid:
            print(f"  Validation error: {serializer.errors.get('cost_per_unit', 'Unknown error')}")
            invalid_failed += 1
        
        print()
    
    print(f"Invalid tests failed (as expected): {invalid_failed}/{len(invalid_test_cases)}")
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 60)
    
    all_valid_passed = valid_passed == len(valid_test_cases)
    all_invalid_failed = invalid_failed == len(invalid_test_cases)
    
    print(f"Valid cases: {valid_passed}/{len(valid_test_cases)} passed")
    print(f"Invalid cases: {invalid_failed}/{len(invalid_test_cases)} failed (as expected)")
    
    if all_valid_passed and all_invalid_failed:
        print("\n🎉 All tests passed! The decimal place validation is working correctly.")
        print("The backend properly accepts values with exactly 2 decimal places")
        print("and rejects values with more than 2 decimal places.")
        return True
    else:
        print("\n⚠️ Some tests failed. The decimal place validation may not be working correctly.")
        return False

if __name__ == '__main__':
    success = test_decimal_validation()
    sys.exit(0 if success else 1) 