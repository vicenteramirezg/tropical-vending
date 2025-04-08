# Generated by Django 4.2 on 2025-04-08 16:56

from django.db import migrations, models
from django.db.models import Count, F


def fix_duplicate_slots(apps, schema_editor):
    """
    Find all items with duplicate slots in each machine and assign unique slots.
    This is a preparatory step before making the slot field unique per machine.
    """
    MachineItemPrice = apps.get_model('core', 'MachineItemPrice')
    db_alias = schema_editor.connection.alias
    
    # Use raw SQL since the slot field might not exist yet
    with schema_editor.connection.cursor() as cursor:
        # Check if slot column exists
        try:
            cursor.execute("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'core_machineitemprice' AND column_name = 'slot'
            """)
            slot_exists = cursor.fetchone() is not None
        except Exception:
            # Catch exception for SQLite which doesn't support information_schema
            try:
                cursor.execute("SELECT slot FROM core_machineitemprice LIMIT 1")
                slot_exists = True
            except Exception:
                slot_exists = False
    
    if not slot_exists:
        # Add the slot column if it doesn't exist
        if 'postgresql' in schema_editor.connection.vendor:
            with schema_editor.connection.cursor() as cursor:
                cursor.execute("ALTER TABLE core_machineitemprice ADD COLUMN slot integer DEFAULT 1")
        else:
            # For SQLite
            with schema_editor.connection.schema_editor() as schema_editor:
                schema_editor.add_field(
                    MachineItemPrice,
                    models.PositiveIntegerField(default=1, null=True, help_text="Numeric slot position in the machine")
                )
    
    # Find machines with duplicate slots
    if 'postgresql' in schema_editor.connection.vendor:
        with schema_editor.connection.cursor() as cursor:
            # For PostgreSQL
            cursor.execute("""
                SELECT machine_id, slot, COUNT(*) 
                FROM core_machineitemprice 
                GROUP BY machine_id, slot 
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            
            for machine_id, slot, count in duplicates:
                # Get all items with this machine_id and slot, ordered by ID
                cursor.execute("""
                    SELECT id FROM core_machineitemprice 
                    WHERE machine_id = %s AND slot = %s 
                    ORDER BY id
                """, [machine_id, slot])
                items = cursor.fetchall()
                
                # Skip the first one (keep its slot) and update the others
                next_slot = -1  # Will be determined dynamically
                
                # Find the highest slot number for this machine
                cursor.execute("""
                    SELECT MAX(slot) FROM core_machineitemprice
                    WHERE machine_id = %s
                """, [machine_id])
                result = cursor.fetchone()
                if result and result[0] is not None:
                    next_slot = result[0] + 1
                else:
                    next_slot = 2  # Start from 2 if no slots exist
                
                # Update the duplicate items with new slots
                for item_id in items[1:]:  # Skip the first item
                    cursor.execute("""
                        UPDATE core_machineitemprice
                        SET slot = %s
                        WHERE id = %s
                    """, [next_slot, item_id[0]])
                    next_slot += 1
    else:
        # For SQLite and other databases, use the ORM approach
        # Get all machineitemprice objects
        all_items = MachineItemPrice.objects.using(db_alias).all()
        
        # Group by machine_id and find duplicates
        machines = {}
        for item in all_items:
            if not hasattr(item, 'slot') or item.slot is None:
                # Initialize slots if they don't exist
                item.slot = 1
                item.save()
                continue
                
            if item.machine_id not in machines:
                machines[item.machine_id] = {}
            
            if item.slot not in machines[item.machine_id]:
                machines[item.machine_id][item.slot] = []
            
            machines[item.machine_id][item.slot].append(item)
        
        # Fix duplicates
        for machine_id, slots in machines.items():
            # Find the highest slot number for this machine
            max_slot = 1
            for slot, items in slots.items():
                if slot and slot > max_slot:
                    max_slot = slot
            
            next_slot = max_slot + 1
            
            # Update duplicates
            for slot, items in slots.items():
                if len(items) > 1:
                    # Skip the first one, update others
                    for item in items[1:]:
                        item.slot = next_slot
                        item.save()
                        next_slot += 1


def reverse_migration(apps, schema_editor):
    """This migration cannot be reversed safely"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_machineitemprice_slot'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_slots, reverse_migration),
    ]
