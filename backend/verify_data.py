import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.db.models import Count
from core.models import MachineItemPrice

def verify_data():
    # Check total items
    total_items = MachineItemPrice.objects.count()
    print(f'Total items: {total_items}')
    
    # Count items by machine
    print('Items by machine:')
    machine_counts = MachineItemPrice.objects.values('machine_id').annotate(count=Count('id')).order_by('machine_id')
    for item in machine_counts:
        print(f"  Machine {item['machine_id']}: {item['count']} items")
    
    # Check for duplicate slots
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT machine_id, slot, COUNT(*) 
            FROM core_machineitemprice 
            GROUP BY machine_id, slot 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
    
    if duplicates:
        print('WARNING: Found duplicate machine/slot combinations:')
        for machine_id, slot, count in duplicates:
            print(f'  Machine {machine_id}, Slot {slot}: {count} items')
    else:
        print('No duplicate machine/slot combinations found.')
    
    # Check for duplicate products in the same machine
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT machine_id, product_id, COUNT(*) 
            FROM core_machineitemprice 
            GROUP BY machine_id, product_id 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
    
    if duplicates:
        print('WARNING: Found duplicate machine/product combinations:')
        for machine_id, product_id, count in duplicates:
            print(f'  Machine {machine_id}, Product {product_id}: {count} items')
    else:
        print('No duplicate machine/product combinations found.')
    
    # Show slots by machine
    print('\nSlots by machine:')
    for machine_id in MachineItemPrice.objects.values_list('machine_id', flat=True).distinct().order_by('machine_id'):
        slots = MachineItemPrice.objects.filter(machine_id=machine_id).values_list('slot', flat=True).order_by('slot')
        print(f'  Machine {machine_id}: {list(slots)}')

if __name__ == "__main__":
    verify_data() 