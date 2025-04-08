import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection, transaction

def fix_duplicate_slots():
    """
    Fix duplicate slot values by finding duplicates and assigning unique slots.
    """
    print("Starting slot fix script...")
    
    with connection.cursor() as cursor:
        try:
            with transaction.atomic():
                # Check database type
                if connection.vendor == 'postgresql':
                    print("Detected PostgreSQL database")
                    
                    # Check if the slot column exists
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='core_machineitemprice' AND column_name='slot'
                    """)
                    
                    column_exists = cursor.fetchone() is not None
                    
                    if not column_exists:
                        print("Slot column doesn't exist yet. Adding it with default values...")
                        # Add the slot column with a default value
                        cursor.execute("""
                            ALTER TABLE core_machineitemprice 
                            ADD COLUMN slot integer DEFAULT 1 NOT NULL
                        """)
                        print("Added slot column with default value 1")
                        
                    # Check for duplicate slots within the same machine
                    cursor.execute("""
                        SELECT machine_id, slot, COUNT(*) 
                        FROM core_machineitemprice 
                        GROUP BY machine_id, slot 
                        HAVING COUNT(*) > 1
                    """)
                    duplicates = cursor.fetchall()
                    
                    if not duplicates:
                        print("No duplicate slots found.")
                    else:
                        print(f"Found {len(duplicates)} machines with duplicate slots.")
                        
                        for machine_id, slot, count in duplicates:
                            print(f"Fixing machine_id={machine_id}, slot={slot} with {count} duplicates")
                            
                            # Find the highest slot number for this machine
                            cursor.execute("""
                                SELECT MAX(slot) FROM core_machineitemprice
                                WHERE machine_id = %s
                            """, [machine_id])
                            
                            max_slot = cursor.fetchone()[0] or 0
                            next_slot = max_slot
                            
                            # Get all items for this machine with this slot
                            cursor.execute("""
                                SELECT id FROM core_machineitemprice
                                WHERE machine_id = %s AND slot = %s
                                ORDER BY id
                            """, [machine_id, slot])
                            
                            items = cursor.fetchall()
                            
                            # Keep the first one, update the rest
                            for i, (item_id,) in enumerate(items[1:], 1):
                                next_slot += 1
                                print(f"  Updated item id={item_id} from slot={slot} to slot={next_slot}")
                                
                                cursor.execute("""
                                    UPDATE core_machineitemprice
                                    SET slot = %s
                                    WHERE id = %s
                                """, [next_slot, item_id])
                    
                    # Create unique index if it doesn't exist
                    cursor.execute("""
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = 'core_machineitemprice_machine_id_slot_92f64367_uniq'
                    """)
                    
                    if not cursor.fetchone():
                        print("Creating unique constraint on machine_id and slot...")
                        try:
                            cursor.execute("""
                                ALTER TABLE core_machineitemprice 
                                ADD CONSTRAINT core_machineitemprice_machine_id_slot_92f64367_uniq 
                                UNIQUE (machine_id, slot)
                            """)
                            print("Unique constraint created successfully")
                        except Exception as e:
                            print(f"Error creating constraint: {e}")
                    else:
                        print("Unique constraint already exists")
                
                else:
                    print(f"Database vendor '{connection.vendor}' not specifically handled.")
                    print("Attempting a generic approach...")
                    
                    # Get all machines
                    cursor.execute("SELECT DISTINCT machine_id FROM core_machineitemprice")
                    machines = cursor.fetchall()
                    
                    for (machine_id,) in machines:
                        # Get all items for this machine
                        cursor.execute("""
                            SELECT id, slot FROM core_machineitemprice
                            WHERE machine_id = %s
                            ORDER BY id
                        """, [machine_id])
                        
                        items = cursor.fetchall()
                        used_slots = set()
                        
                        for item_id, slot in items:
                            if slot in used_slots:
                                # Find next available slot
                                next_slot = 1
                                while next_slot in used_slots:
                                    next_slot += 1
                                
                                # Update with the new slot
                                cursor.execute("""
                                    UPDATE core_machineitemprice
                                    SET slot = %s
                                    WHERE id = %s
                                """, [next_slot, item_id])
                                
                                print(f"Updated machine_id={machine_id}, item_id={item_id} to slot={next_slot}")
                                used_slots.add(next_slot)
                            else:
                                used_slots.add(slot)
            
            print("Slot fix completed successfully.")
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = fix_duplicate_slots()
    sys.exit(0 if success else 1) 