from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import Django's auth views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('machines/', include('machines.urls', namespace='machines')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('visits/', include('visits.urls', namespace='visits')),
    path('', include('home.urls')),  # Set the home app as the homepage
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Login view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout view
]