from django.contrib import admin
from core.models import (
    Location, Machine, Product, MachineItemPrice,
    WholesalePurchase, Visit, VisitMachineRestock, RestockEntry
)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_at')
    search_fields = ('name', 'address')

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('machine_type', 'model', 'location', 'created_at')
    list_filter = ('machine_type', 'location')
    search_fields = ('machine_type', 'model', 'location__name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_type', 'average_cost', 'created_at')
    list_filter = ('unit_type',)
    search_fields = ('name',)

@admin.register(MachineItemPrice)
class MachineItemPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'machine', 'price', 'current_stock', 'profit_margin')
    list_filter = ('machine', 'product')
    search_fields = ('product__name', 'machine__machine_type')

@admin.register(WholesalePurchase)
class WholesalePurchaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'total_cost', 'unit_cost', 'purchased_at')
    list_filter = ('product', 'purchased_at')
    search_fields = ('product__name',)

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('location', 'user', 'visit_date', 'created_at')
    list_filter = ('location', 'user', 'visit_date')
    search_fields = ('location__name', 'user__username')

@admin.register(VisitMachineRestock)
class VisitMachineRestockAdmin(admin.ModelAdmin):
    list_display = ('visit', 'machine', 'created_at')
    list_filter = ('visit__location', 'machine')
    search_fields = ('visit__location__name', 'machine__machine_type')

@admin.register(RestockEntry)
class RestockEntryAdmin(admin.ModelAdmin):
    list_display = ('product', 'visit_machine_info', 'stock_before', 'restocked', 'total_after')
    list_filter = ('product', 'visit_machine_restock__machine', 'visit_machine_restock__visit__location')
    search_fields = ('product__name', 'visit_machine_restock__machine__machine_type')
    
    def visit_machine_info(self, obj):
        return f"{obj.visit_machine_restock.machine} on {obj.visit_machine_restock.visit.visit_date.date()}"
    
    def total_after(self, obj):
        return obj.stock_before + obj.restocked 