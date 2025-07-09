#!/usr/bin/env python3
"""
Test script to verify the wholesale purchase serializer fix.
This script simulates the serializer validation that was failing.
"""

import os
import sys
import django
from decimal import Decimal

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

from core.models import Product, Supplier, WholesalePurchase
from core.serializers.wholesale_purchase_serializer import WholesalePurchaseSerializer
from django.utils import timezone

def test_supplier_validation():
    """Test the supplier validation fix"""
    print("Testing supplier validation...")
    
    # Create a test supplier if it doesn't exist
    supplier, created = Supplier.objects.get_or_create(
        name="Test Supplier",
        defaults={
            'contact_person': 'John Doe',
            'phone': '123-456-7890',
            'email': 'test@supplier.com',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created test supplier: {supplier}")
    else:
        print(f"Using existing supplier: {supplier}")
    
    # Create a test product if it doesn't exist
    product, created = Product.objects.get_or_create(
        name="Test Product",
        defaults={
            'unit_type': 'piece',
            'inventory_quantity': 0,
            'product_type': 'Soda'
        }
    )
    
    if created:
        print(f"Created test product: {product}")
    else:
        print(f"Using existing product: {product}")
    
    # Test data that was causing the error
    test_data = {
        'product': product.id,
        'supplier': supplier.id,  # This should be an integer ID
        'purchased_at': timezone.now().isoformat(),
        'purchase_date': timezone.now().isoformat(),
        'quantity': 10,
        'total_cost': '15.00',
        'notes': 'Test purchase',
        'cost_per_unit': '1.50'
    }
    
    print(f"Test data: {test_data}")
    
    # Test the serializer
    try:
        serializer = WholesalePurchaseSerializer(data=test_data)
        print(f"Initial data: {serializer.initial_data}")
        print(f"Validating...")
        
        if serializer.is_valid():
            print("✅ Serializer validation passed!")
            print(f"Validated data: {serializer.validated_data}")
            
            # Try to save the purchase
            purchase = serializer.save()
            print(f"✅ Purchase created successfully: {purchase}")
            
            # Clean up - delete the test purchase
            purchase.delete()
            print("✅ Test purchase cleaned up")
            
            return True
        else:
            print(f"❌ Serializer validation failed: {serializer.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Error during serializer test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases for supplier validation"""
    print("\nTesting edge cases...")
    
    # Get a product for testing
    product = Product.objects.first()
    if not product:
        print("❌ No product found for testing")
        return False
    
    # Test with None supplier
    test_data_none = {
        'product': product.id,
        'supplier': None,
        'purchased_at': timezone.now().isoformat(),
        'quantity': 5,
        'total_cost': '10.00',
    }
    
    try:
        serializer = WholesalePurchaseSerializer(data=test_data_none)
        if serializer.is_valid():
            print("✅ None supplier validation passed")
        else:
            print(f"❌ None supplier validation failed: {serializer.errors}")
    except Exception as e:
        print(f"❌ Error with None supplier: {e}")
    
    # Test with empty string supplier
    test_data_empty = {
        'product': product.id,
        'supplier': '',
        'purchased_at': timezone.now().isoformat(),
        'quantity': 5,
        'total_cost': '10.00',
    }
    
    try:
        serializer = WholesalePurchaseSerializer(data=test_data_empty)
        if serializer.is_valid():
            print("✅ Empty supplier validation passed")
        else:
            print(f"❌ Empty supplier validation failed: {serializer.errors}")
    except Exception as e:
        print(f"❌ Error with empty supplier: {e}")
    
    # Test with invalid supplier ID
    test_data_invalid = {
        'product': product.id,
        'supplier': 99999,  # Non-existent ID
        'purchased_at': timezone.now().isoformat(),
        'quantity': 5,
        'total_cost': '10.00',
    }
    
    try:
        serializer = WholesalePurchaseSerializer(data=test_data_invalid)
        if serializer.is_valid():
            print("❌ Invalid supplier validation should have failed")
        else:
            print("✅ Invalid supplier correctly rejected")
    except Exception as e:
        print(f"❌ Error with invalid supplier: {e}")

if __name__ == "__main__":
    print("Starting wholesale purchase serializer tests...\n")
    
    success = test_supplier_validation()
    test_edge_cases()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Please check the output above.") 