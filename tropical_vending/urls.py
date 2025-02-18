from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('machines/', include('machines.urls', namespace='machines')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('visits/', include('visits.urls', namespace='visits')),
    path('', include('home.urls')),  # Set the home app as the homepage
]