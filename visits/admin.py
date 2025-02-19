from django.contrib import admin
from .models import Visit, MachineRefill

class MachineRefillInline(admin.TabularInline):
    model = MachineRefill
    extra = 1  # Number of empty forms to display

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('location', 'date_visited')
    inlines = [MachineRefillInline]

@admin.register(MachineRefill)
class MachineRefillAdmin(admin.ModelAdmin):
    list_display = ('visit', 'vending_machine', 'product', 'units_added')