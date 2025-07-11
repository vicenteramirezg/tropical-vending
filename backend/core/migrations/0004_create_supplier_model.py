# Generated by Django 4.2.20 on 2025-07-07 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_route_to_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Supplier name (e.g., Walmart, Sams Club)', max_length=100, unique=True)),
                ('contact_person', models.CharField(blank=True, default='', help_text='Primary contact person', max_length=100)),
                ('phone', models.CharField(blank=True, default='', help_text='Contact phone number', max_length=20)),
                ('email', models.EmailField(blank=True, default='', help_text='Contact email address', max_length=254)),
                ('address', models.TextField(blank=True, default='', help_text='Supplier address')),
                ('notes', models.TextField(blank=True, default='', help_text='Additional notes about the supplier')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this supplier is currently active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
                'indexes': [models.Index(fields=['name'], name='core_suppli_name_c90f73_idx'), models.Index(fields=['is_active'], name='core_suppli_is_acti_29603b_idx'), models.Index(fields=['created_at'], name='core_suppli_created_edc53d_idx')],
            },
        ),
    ]
