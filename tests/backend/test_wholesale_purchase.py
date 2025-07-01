import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timezone
from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

from core.models import Product, WholesalePurchase, ProductCost
from core.serializers import WholesalePurchaseSerializer


class WholesalePurchaseModelTest(TestCase):
    """Test the WholesalePurchase model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(
            name="Test Coke",
            product_type="Soda",
            unit_type="can",
            inventory_quantity=0
        )
    
    def test_create_wholesale_purchase(self):
        """Test creating a wholesale purchase"""
        purchase = WholesalePurchase.objects.create(
            product=self.product,
            quantity=24,
            total_cost=Decimal('12.00'),
            purchased_at=datetime.now(timezone.utc),
            supplier="Test Supplier",
            notes="Test purchase"
        )
        
        self.assertEqual(purchase.product, self.product)
        self.assertEqual(purchase.quantity, 24)
        self.assertEqual(purchase.total_cost, Decimal('12.00'))
        self.assertEqual(purchase.unit_cost, Decimal('0.50'))
        self.assertEqual(purchase.supplier, "Test Supplier")
        self.assertFalse(purchase.inventory_updated)
    
    def test_unit_cost_calculation(self):
        """Test that unit cost is calculated correctly"""
        purchase = WholesalePurchase.objects.create(
            product=self.product,
            quantity=3,
            total_cost=Decimal('10.00'),
            purchased_at=datetime.now(timezone.utc)
        )
        
        # Should be 10.00 / 3 = 3.33 (rounded to 2 decimal places)
        expected_unit_cost = Decimal('10.00') / Decimal('3')
        self.assertEqual(purchase.unit_cost, expected_unit_cost.quantize(Decimal('0.01')))
    
    def test_unit_cost_with_complex_division(self):
        """Test unit cost calculation with numbers that result in repeating decimals"""
        purchase = WholesalePurchase.objects.create(
            product=self.product,
            quantity=7,
            total_cost=Decimal('20.00'),
            purchased_at=datetime.now(timezone.utc)
        )
        
        # Should be 20.00 / 7 = 2.857142... which should be handled properly
        expected_unit_cost = Decimal('20.00') / Decimal('7')
        self.assertEqual(purchase.unit_cost, expected_unit_cost)
    
    def test_inventory_update(self):
        """Test that inventory is updated correctly"""
        initial_inventory = self.product.inventory_quantity
        
        purchase = WholesalePurchase.objects.create(
            product=self.product,
            quantity=50,
            total_cost=Decimal('25.00'),
            purchased_at=datetime.now(timezone.utc)
        )
        
        # Update inventory
        purchase.update_inventory()
        
        # Refresh product from database
        self.product.refresh_from_db()
        
        self.assertEqual(self.product.inventory_quantity, initial_inventory + 50)
        self.assertTrue(purchase.inventory_updated)
        
        # Check that ProductCost record was created
        cost_record = ProductCost.objects.filter(purchase=purchase).first()
        self.assertIsNotNone(cost_record)
        self.assertEqual(cost_record.unit_cost, purchase.unit_cost)
        self.assertEqual(cost_record.total_cost, purchase.total_cost)


class WholesalePurchaseSerializerTest(TestCase):
    """Test the WholesalePurchaseSerializer functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(
            name="Test Sprite",
            product_type="Soda",
            unit_type="can",
            inventory_quantity=10
        )
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'product': self.product.id,
            'quantity': 24,
            'total_cost': '12.00',
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'Test Supplier',
            'notes': 'Test notes'
        }
        
        serializer = WholesalePurchaseSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        purchase = serializer.save()
        self.assertEqual(purchase.quantity, 24)
        self.assertEqual(purchase.total_cost, Decimal('12.00'))
        self.assertEqual(purchase.unit_cost, Decimal('0.50'))
    
    def test_serializer_with_cost_per_unit(self):
        """Test serializer when cost_per_unit is provided"""
        data = {
            'product': self.product.id,
            'quantity': 10,
            'cost_per_unit': '1.50',  # This should calculate total_cost as 15.00
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'Test Supplier'
        }
        
        serializer = WholesalePurchaseSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        purchase = serializer.save()
        self.assertEqual(purchase.quantity, 10)
        self.assertEqual(purchase.total_cost, Decimal('15.00'))
        self.assertEqual(purchase.unit_cost, Decimal('1.50'))
    
    def test_serializer_with_cost_per_unit_two_decimals(self):
        """Test serializer with cost_per_unit that has exactly 2 decimal places"""
        data = {
            'product': self.product.id,
            'quantity': 3,
            'cost_per_unit': '3.33',  # Exactly 2 decimal places
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'Test Supplier'
        }
        
        serializer = WholesalePurchaseSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        purchase = serializer.save()
        self.assertEqual(purchase.quantity, 3)
        self.assertEqual(purchase.total_cost, Decimal('9.99'))  # 3 * 3.33
        self.assertEqual(purchase.unit_cost, Decimal('3.33'))
    
    def test_serializer_rejects_too_many_decimal_places(self):
        """Test that serializer rejects cost_per_unit with more than 2 decimal places"""
        data = {
            'product': self.product.id,
            'quantity': 3,
            'cost_per_unit': '3.333',  # Too many decimal places
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'Test Supplier'
        }
        
        serializer = WholesalePurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cost_per_unit', serializer.errors)
        self.assertIn('Ensure that there are no more than 2 decimal places', str(serializer.errors['cost_per_unit']))
    
    def test_serializer_rejects_too_many_digits(self):
        """Test that serializer rejects cost_per_unit with too many total digits"""
        data = {
            'product': self.product.id,
            'quantity': 1,
            'cost_per_unit': '12345678901.00',  # Too many total digits (more than 10)
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'Test Supplier'
        }
        
        serializer = WholesalePurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cost_per_unit', serializer.errors)


class WholesalePurchaseAPITest(APITestCase):
    """Test the WholesalePurchase API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(
            name="Test Pepsi",
            product_type="Soda",
            unit_type="can",
            inventory_quantity=5
        )
    
    def test_create_purchase_via_api(self):
        """Test creating a purchase via API"""
        data = {
            'product': self.product.id,
            'quantity': 12,
            'total_cost': '6.00',
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'API Test Supplier',
            'notes': 'Created via API'
        }
        
        response = self.client.post('/api/purchases/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that purchase was created
        purchase = WholesalePurchase.objects.get(id=response.data['id'])
        self.assertEqual(purchase.quantity, 12)
        self.assertEqual(purchase.total_cost, Decimal('6.00'))
        self.assertEqual(purchase.unit_cost, Decimal('0.50'))
    
    def test_create_purchase_with_cost_per_unit_via_api(self):
        """Test creating a purchase with cost_per_unit via API"""
        data = {
            'product': self.product.id,
            'quantity': 8,
            'cost_per_unit': '0.75',
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'API Test Supplier'
        }
        
        response = self.client.post('/api/purchases/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that total_cost was calculated correctly
        purchase = WholesalePurchase.objects.get(id=response.data['id'])
        self.assertEqual(purchase.quantity, 8)
        self.assertEqual(purchase.total_cost, Decimal('6.00'))  # 8 * 0.75
        self.assertEqual(purchase.unit_cost, Decimal('0.75'))
    
    def test_create_purchase_with_invalid_cost_per_unit_via_api(self):
        """Test that API rejects cost_per_unit with too many decimal places"""
        data = {
            'product': self.product.id,
            'quantity': 3,
            'cost_per_unit': '1.333',  # Too many decimal places
            'purchased_at': '2024-01-15T12:00:00Z',
            'supplier': 'API Test Supplier'
        }
        
        response = self.client.post('/api/purchases/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cost_per_unit', response.data)
        self.assertIn('Ensure that there are no more than 2 decimal places', str(response.data['cost_per_unit']))
    
    def test_update_purchase_via_api(self):
        """Test updating a purchase via API"""
        # Create initial purchase
        purchase = WholesalePurchase.objects.create(
            product=self.product,
            quantity=10,
            total_cost=Decimal('5.00'),
            purchased_at=datetime.now(timezone.utc),
            supplier="Original Supplier"
        )
        
        # Update via API
        data = {
            'product': self.product.id,
            'quantity': 15,
            'total_cost': '9.00',
            'purchased_at': purchase.purchased_at.isoformat(),
            'supplier': 'Updated Supplier',
            'notes': 'Updated via API'
        }
        
        response = self.client.put(f'/api/purchases/{purchase.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that purchase was updated
        purchase.refresh_from_db()
        self.assertEqual(purchase.quantity, 15)
        self.assertEqual(purchase.total_cost, Decimal('9.00'))
        self.assertEqual(purchase.unit_cost, Decimal('0.60'))
        self.assertEqual(purchase.supplier, 'Updated Supplier')
    
    def test_list_purchases_via_api(self):
        """Test listing purchases via API"""
        # Create test purchases
        WholesalePurchase.objects.create(
            product=self.product,
            quantity=5,
            total_cost=Decimal('2.50'),
            purchased_at=datetime.now(timezone.utc),
            supplier="Supplier 1"
        )
        WholesalePurchase.objects.create(
            product=self.product,
            quantity=10,
            total_cost=Decimal('8.00'),
            purchased_at=datetime.now(timezone.utc),
            supplier="Supplier 2"
        )
        
        response = self.client.get('/api/purchases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check that unit costs are included in response
        for purchase_data in response.data:
            self.assertIn('unit_cost', purchase_data)
            self.assertIn('cost_per_unit', purchase_data)  # Should be mapped from unit_cost
    
    def test_delete_purchase_via_api(self):
        """Test deleting a purchase via API"""
        purchase = WholesalePurchase.objects.create(
            product=self.product,
            quantity=6,
            total_cost=Decimal('3.00'),
            purchased_at=datetime.now(timezone.utc),
            supplier="To Delete Supplier"
        )
        
        response = self.client.delete(f'/api/purchases/{purchase.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that purchase was deleted
        self.assertFalse(WholesalePurchase.objects.filter(id=purchase.id).exists())


class DecimalPlacesEdgeCaseTest(TestCase):
    """Test edge cases specifically related to decimal place handling"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(
            name="Edge Case Product",
            product_type="Soda",
            unit_type="can",
            inventory_quantity=0
        )
    
    def test_division_resulting_in_repeating_decimals(self):
        """Test cases where division results in repeating decimals"""
        test_cases = [
            (10, Decimal('3.00')),  # 3.00 / 10 = 0.30
            (3, Decimal('10.00')),  # 10.00 / 3 = 3.333...
            (7, Decimal('20.00')),  # 20.00 / 7 = 2.857142...
            (6, Decimal('5.00')),   # 5.00 / 6 = 0.833...
        ]
        
        for quantity, total_cost in test_cases:
            with self.subTest(quantity=quantity, total_cost=total_cost):
                purchase = WholesalePurchase.objects.create(
                    product=self.product,
                    quantity=quantity,
                    total_cost=total_cost,
                    purchased_at=datetime.now(timezone.utc)
                )
                
                # Unit cost should be calculated without issues
                expected_unit_cost = total_cost / quantity
                self.assertEqual(purchase.unit_cost, expected_unit_cost)
                
                # Should be able to serialize without issues
                serializer = WholesalePurchaseSerializer(purchase)
                data = serializer.data
                self.assertIn('unit_cost', data)
                self.assertIn('cost_per_unit', data)
    
    def test_serializer_with_edge_case_cost_per_unit_values(self):
        """Test serializer with edge case cost_per_unit values"""
        edge_cases = [
            '0.01',    # Minimum valid value
            '0.99',    # Just under 1
            '1.00',    # Exactly 1
            '999.99',  # Large value with 2 decimal places
        ]
        
        for cost_per_unit in edge_cases:
            with self.subTest(cost_per_unit=cost_per_unit):
                data = {
                    'product': self.product.id,
                    'quantity': 1,
                    'cost_per_unit': cost_per_unit,
                    'purchased_at': '2024-01-15T12:00:00Z',
                    'supplier': 'Edge Case Supplier'
                }
                
                serializer = WholesalePurchaseSerializer(data=data)
                self.assertTrue(serializer.is_valid(), f"Failed for {cost_per_unit}: {serializer.errors}")
                
                purchase = serializer.save()
                self.assertEqual(str(purchase.unit_cost), cost_per_unit)


if __name__ == '__main__':
    import unittest
    unittest.main() 