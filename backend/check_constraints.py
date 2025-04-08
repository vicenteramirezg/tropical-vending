import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def check_constraints():
    with connection.cursor() as cursor:
        # Check unique constraints
        cursor.execute("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conrelid = 'core_machineitemprice'::regclass AND contype = 'u'
        """)
        constraints = cursor.fetchall()
        print('Unique constraints:', constraints)

        # Check if machine_id and slot have a unique constraint
        cursor.execute("""
            SELECT con.conname, att_a.attname as col_a, att_b.attname as col_b
            FROM pg_constraint con
            JOIN pg_attribute att_a ON att_a.attnum = ANY(con.conkey) AND att_a.attrelid = con.conrelid
            JOIN pg_attribute att_b ON att_b.attnum = ANY(con.conkey) AND att_b.attrelid = con.conrelid
            WHERE con.conrelid = 'core_machineitemprice'::regclass 
            AND con.contype = 'u'
            AND att_a.attname = 'machine_id'
            AND att_b.attname = 'slot'
        """)
        slot_constraint = cursor.fetchall()
        if slot_constraint:
            print('Machine ID and slot have a unique constraint:', slot_constraint)
        else:
            print('No unique constraint for machine_id and slot')

if __name__ == "__main__":
    check_constraints() 