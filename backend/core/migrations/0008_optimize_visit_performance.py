# Generated migration for visit performance optimizations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_supplier_foreign_key'),
    ]

    operations = [
        # Add composite indexes for common query patterns in visit operations
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_visit_location_date ON core_visit(location_id, visit_date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_visit_location_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_visit_user_date ON core_visit(user_id, visit_date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_visit_user_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_restock_entry_visit_machine ON core_restockentry(visit_machine_restock_id, product_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_restock_entry_visit_machine;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_machine_item_machine_product ON core_machineitemprice(machine_id, product_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_machine_item_machine_product;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_visit_machine_restock_visit ON core_visitmachinerestock(visit_id, machine_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_visit_machine_restock_visit;"
        ),
    ]
