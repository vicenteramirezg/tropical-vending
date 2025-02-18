from django.contrib import admin
from .models import Product, StockRecord

admin.site.register(Product)
admin.site.register(StockRecord)