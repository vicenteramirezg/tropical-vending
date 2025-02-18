from django.urls import path
from . import views

app_name = 'machines'

urlpatterns = [
    path('', views.VendingMachineListView.as_view(), name='list'),
    path('<int:pk>/', views.VendingMachineDetailView.as_view(), name='detail'),
    path('create/', views.VendingMachineCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.VendingMachineUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.VendingMachineDeleteView.as_view(), name='delete'),
]