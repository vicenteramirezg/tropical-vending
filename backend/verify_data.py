"""
Script to verify the data in the database.
Run this script from the backend directory using:
python verify_data.py
"""
import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

# Now we can import Django models
from core.models import Location, Machine, Product, WholesalePurchase, ProductCost

def check_locations():
    """Check locations in the database"""
    print("\n=== LOCATIONS ===")
    locations = Location.objects.all()
    for location in locations:
        print(f"ID: {location.id}, Name: {location.name}, Address: {location.address}")
    print(f"Total locations: {locations.count()}")

def check_machines():
    """Check machines in the database"""
    print("\n=== MACHINES ===")
    machines = Machine.objects.all().select_related('location')
    for machine in machines:
        print(f"ID: {machine.id}, Name: {machine.name}, Type: {machine.machine_type}, Location: {machine.location.name}")
    print(f"Total machines: {machines.count()}")

def check_products():
    """Check products in the database"""
    print("\n=== PRODUCTS ===")
    products = Product.objects.all()
    for product in products:
        print(f"ID: {product.id}, Name: {product.name}, Type: {product.product_type}, " 
              f"Inventory: {product.inventory_quantity}, Latest Cost: ${product.latest_unit_cost}, "
              f"Average Cost: ${product.average_cost}")
    print(f"Total products: {products.count()}")

def check_purchases():
    """Check wholesale purchases in the database"""
    print("\n=== WHOLESALE PURCHASES ===")
    purchases = WholesalePurchase.objects.all().select_related('product')
    for purchase in purchases:
        print(f"ID: {purchase.id}, Product: {purchase.product.name}, Quantity: {purchase.quantity}, "
              f"Total Cost: ${purchase.total_cost}, Unit Cost: ${purchase.unit_cost}, "
              f"Supplier: {purchase.supplier}, Date: {purchase.purchased_at.date()}")
    print(f"Total purchases: {purchases.count()}")

def check_costs():
    """Check product cost history in the database"""
    print("\n=== PRODUCT COSTS ===")
    costs = ProductCost.objects.all().select_related('product')
    for cost in costs:
        print(f"ID: {cost.id}, Product: {cost.product.name}, Date: {cost.date.date()}, " 
              f"Quantity: {cost.quantity}, Unit Cost: ${cost.unit_cost}, Total: ${cost.total_cost}")
    print(f"Total cost records: {costs.count()}")

def main():
    """Main function to verify database data"""
    print("Starting database verification...")
    
    # Check all data
    check_locations()
    check_machines()
    check_products()
    check_purchases()
    check_costs()
    
    print("\nDatabase verification completed!")

if __name__ == "__main__":
    main() 