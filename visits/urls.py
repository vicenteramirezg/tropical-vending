from django.urls import path
from . import views

app_name = 'visits'

urlpatterns = [
    path('', views.VisitListView.as_view(), name='list'),
    path('<int:pk>/', views.VisitDetailView.as_view(), name='detail'),
    path('create/', views.VisitCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.VisitUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.VisitDeleteView.as_view(), name='delete'),
]