# Generated by Django 4.2 on 2025-03-31 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='name',
            field=models.CharField(default='Machine', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='machine',
            name='machine_type',
            field=models.CharField(choices=[('Snack', 'Snack'), ('Soda', 'Soda'), ('Combo', 'Combo')], max_length=100),
        ),
        migrations.AlterField(
            model_name='machine',
            name='model',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
