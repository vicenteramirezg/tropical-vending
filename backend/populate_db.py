"""
Script to populate the SQLite database with sample data.
Run this script from the backend directory using:
python populate_db.py
"""
import os
import sys
import django
from decimal import Decimal
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

# Now we can import Django models
from core.models import Location, Machine, Product, WholesalePurchase

def create_locations():
    """Create sample locations"""
    locations = [
        {
            'name': 'Downtown Office Building',
            'address': '123 Main Street, Downtown'
        },
        {
            'name': 'University Campus',
            'address': '456 Campus Drive, College Town'
        },
        {
            'name': 'Shopping Mall',
            'address': '789 Retail Avenue, Westside'
        }
    ]
    
    created_locations = []
    for location_data in locations:
        location, created = Location.objects.get_or_create(**location_data)
        print(f"{'Created' if created else 'Found'} location: {location.name}")
        created_locations.append(location)
    
    return created_locations

def create_machines(locations):
    """Create sample machines at each location"""
    machines = [
        {
            'name': 'Drink Machine 1',
            'location': locations[0],
            'machine_type': 'Soda',
            'model': 'VendTech 5000'
        },
        {
            'name': 'Snack Machine 1',
            'location': locations[0],
            'machine_type': 'Snack',
            'model': 'SnackMaster Pro'
        },
        {
            'name': 'Combo Machine 1',
            'location': locations[1],
            'machine_type': 'Combo',
            'model': 'OmniVend Deluxe'
        },
        {
            'name': 'Drink Machine 2',
            'location': locations[2],
            'machine_type': 'Soda',
            'model': 'VendTech 4000'
        }
    ]
    
    created_machines = []
    for machine_data in machines:
        machine, created = Machine.objects.get_or_create(**machine_data)
        print(f"{'Created' if created else 'Found'} machine: {machine.name} at {machine.location.name}")
        created_machines.append(machine)
    
    return created_machines

def create_products():
    """Create sample products"""
    products = [
        {
            'name': 'Coca Cola',
            'product_type': 'Soda',
            'unit_type': 'can',
            'image_url': 'https://example.com/images/coke.jpg'
        },
        {
            'name': 'Diet Coke',
            'product_type': 'Soda',
            'unit_type': 'can',
            'image_url': 'https://example.com/images/diet_coke.jpg'
        },
        {
            'name': 'Sprite',
            'product_type': 'Soda',
            'unit_type': 'can',
            'image_url': 'https://example.com/images/sprite.jpg'
        },
        {
            'name': 'Lays Classic',
            'product_type': 'Snack',
            'unit_type': 'bag',
            'image_url': 'https://example.com/images/lays.jpg'
        },
        {
            'name': 'Doritos Nacho Cheese',
            'product_type': 'Snack',
            'unit_type': 'bag',
            'image_url': 'https://example.com/images/doritos.jpg'
        },
        {
            'name': 'Snickers',
            'product_type': 'Snack',
            'unit_type': 'bar',
            'image_url': 'https://example.com/images/snickers.jpg'
        },
        {
            'name': 'Water Bottle',
            'product_type': 'Soda',
            'unit_type': 'bottle',
            'image_url': 'https://example.com/images/water.jpg'
        }
    ]
    
    created_products = []
    for product_data in products:
        product, created = Product.objects.get_or_create(**product_data)
        print(f"{'Created' if created else 'Found'} product: {product.name}")
        created_products.append(product)
    
    return created_products

def create_purchases(products):
    """Create wholesale purchases for products to establish inventory and costs"""
    # Current date for purchase records
    now = timezone.now()
    
    purchases = [
        # Soda purchases
        {
            'product': next(p for p in products if p.name == 'Coca Cola'),
            'quantity': 100,
            'total_cost': Decimal('35.00'),  # $0.35 per can
            'purchased_at': now,
            'supplier': 'Sams',
            'notes': 'Initial stock'
        },
        {
            'product': next(p for p in products if p.name == 'Diet Coke'),
            'quantity': 80,
            'total_cost': Decimal('28.00'),  # $0.35 per can
            'purchased_at': now,
            'supplier': 'Sams',
            'notes': 'Initial stock'
        },
        {
            'product': next(p for p in products if p.name == 'Sprite'),
            'quantity': 60,
            'total_cost': Decimal('21.00'),  # $0.35 per can
            'purchased_at': now,
            'supplier': 'Sams',
            'notes': 'Initial stock'
        },
        {
            'product': next(p for p in products if p.name == 'Water Bottle'),
            'quantity': 120,
            'total_cost': Decimal('60.00'),  # $0.50 per bottle
            'purchased_at': now,
            'supplier': 'Star',
            'notes': 'Initial stock'
        },
        
        # Snack purchases
        {
            'product': next(p for p in products if p.name == 'Lays Classic'),
            'quantity': 50,
            'total_cost': Decimal('37.50'),  # $0.75 per bag
            'purchased_at': now,
            'supplier': 'Star',
            'notes': 'Initial stock'
        },
        {
            'product': next(p for p in products if p.name == 'Doritos Nacho Cheese'),
            'quantity': 50,
            'total_cost': Decimal('40.00'),  # $0.80 per bag
            'purchased_at': now,
            'supplier': 'Star',
            'notes': 'Initial stock'
        },
        {
            'product': next(p for p in products if p.name == 'Snickers'),
            'quantity': 60,
            'total_cost': Decimal('30.00'),  # $0.50 per bar
            'purchased_at': now,
            'supplier': 'Star',
            'notes': 'Initial stock'
        }
    ]
    
    for purchase_data in purchases:
        product = purchase_data['product']
        quantity = purchase_data['quantity']
        total_cost = purchase_data['total_cost']
        unit_cost = total_cost / quantity
        
        purchase = WholesalePurchase.objects.create(**purchase_data)
        print(f"Created purchase: {quantity} {product.unit_type}(s) of {product.name} at ${unit_cost:.2f} each (${total_cost})")

def main():
    """Main function to populate the database"""
    print("Starting database population...")
    
    # Create sample data
    locations = create_locations()
    machines = create_machines(locations)
    products = create_products()
    create_purchases(products)
    
    print("\nDatabase population completed!")

if __name__ == "__main__":
    main() 