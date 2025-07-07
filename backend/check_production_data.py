#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

from django.db import connection

def check_production_data():
    """Check what data exists in production"""
    print("Checking production data...")
    
    with connection.cursor() as cursor:
        # Check wholesale purchases
        cursor.execute("SELECT id, supplier_id, supplier_name FROM core_wholesalepurchase")
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} wholesale purchases:")
        for row in rows:
            print(f"  ID {row[0]}: supplier_id={row[1]}, supplier_name='{row[2]}'")
        
        # Check suppliers
        cursor.execute("SELECT id, name FROM core_supplier")
        suppliers = cursor.fetchall()
        
        print(f"\nFound {len(suppliers)} suppliers:")
        for supplier in suppliers:
            print(f"  ID {supplier[0]}: name='{supplier[1]}'")

if __name__ == "__main__":
    check_production_data() 