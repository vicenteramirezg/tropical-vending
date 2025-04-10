# Generated by Django 4.2 on 2025-04-08 16:34

from django.db import migrations
from collections import defaultdict


def assign_unique_slots(apps, schema_editor):
    """
    Find all MachineItemPrice records with duplicate machine/slot combinations
    and assign them unique slot numbers.
    """
    MachineItemPrice = apps.get_model('core', 'MachineItemPrice')
    
    # Group machine items by machine
    machine_items = defaultdict(list)
    for item in MachineItemPrice.objects.all():
        machine_items[item.machine_id].append(item)
    
    # For each machine, fix duplicate slots
    for machine_id, items in machine_items.items():
        # Get all used slots for this machine
        used_slots = set()
        slot_to_items = defaultdict(list)
        
        # Group items by slot to find duplicates
        for item in items:
            slot_to_items[item.slot].append(item)
            used_slots.add(item.slot)
        
        # Find the next available slot number
        next_slot = 1
        while next_slot in used_slots:
            next_slot += 1
        
        # Fix duplicate slots
        for slot, duplicates in slot_to_items.items():
            # Skip if there's only one item with this slot
            if len(duplicates) <= 1:
                continue
                
            # Keep the first item with original slot, reassign others
            for i in range(1, len(duplicates)):
                item = duplicates[i]
                print(f"Reassigning machine {machine_id}, product {item.product_id} from slot {item.slot} to {next_slot}")
                item.slot = next_slot
                item.save()
                
                # Update next available slot
                used_slots.add(next_slot)
                next_slot += 1
                while next_slot in used_slots:
                    next_slot += 1


def reverse_migration(apps, schema_editor):
    """
    This migration cannot be reversed safely
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_machineitemprice_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(assign_unique_slots, reverse_migration),
    ]
