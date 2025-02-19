from django.contrib import admin
from .models import Location, VendingMachine

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')

@admin.register(VendingMachine)
class VendingMachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'last_visited')