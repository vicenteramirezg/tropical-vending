from django.urls import path
from . import views

app_name = 'machines'

urlpatterns = [
    # Location URLs
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/update/', views.LocationUpdateView.as_view(), name='location_update'),
    path('locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),
    # VendingMachine URLs
    path('', views.VendingMachineListView.as_view(), name='list'),
    path('<int:pk>/', views.VendingMachineDetailView.as_view(), name='detail'),
    path('create/', views.VendingMachineCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.VendingMachineUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.VendingMachineDeleteView.as_view(), name='delete'),
]