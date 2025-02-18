from django.contrib import admin
from .models import Location, VendingMachine

admin.site.register(Location)
admin.site.register(VendingMachine)