import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection, transaction

def add_slot_constraint():
    with connection.cursor() as cursor:
        try:
            with transaction.atomic():
                print("Adding unique constraint for machine_id and slot...")
                
                # Check if the constraint already exists
                cursor.execute("""
                    SELECT 1 FROM pg_constraint 
                    WHERE conrelid = 'core_machineitemprice'::regclass 
                    AND conname = 'core_machineitemprice_machine_id_slot_92f64367_uniq'
                """)
                
                if cursor.fetchone():
                    print("Constraint already exists.")
                    return
                
                # Add the unique constraint
                cursor.execute("""
                    ALTER TABLE core_machineitemprice 
                    ADD CONSTRAINT core_machineitemprice_machine_id_slot_92f64367_uniq 
                    UNIQUE (machine_id, slot)
                """)
                
                print("Unique constraint added successfully.")
                
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    add_slot_constraint() 