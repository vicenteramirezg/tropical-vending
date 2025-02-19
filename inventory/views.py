from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/list.html'
    context_object_name = 'products'
    login_url = '/login/'  # Redirect to login if not authenticated

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/detail.html'
    login_url = '/login/'  # Redirect to login if not authenticated

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'inventory/form.html'
    fields = ['name', 'barcode']
    success_url = reverse_lazy('inventory:list')
    login_url = '/login/'  # Redirect to login if not authenticated

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'inventory/form.html'
    fields = ['name', 'barcode']
    success_url = reverse_lazy('inventory:list')
    login_url = '/login/'  # Redirect to login if not authenticated

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/confirm_delete.html'
    success_url = reverse_lazy('inventory:list')
    login_url = '/login/'  # Redirect to login if not authenticated