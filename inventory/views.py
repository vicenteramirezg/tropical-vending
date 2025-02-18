from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'inventory/list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = Product
    template_name = 'inventory/detail.html'

class ProductCreateView(CreateView):
    model = Product
    template_name = 'inventory/form.html'
    fields = ['name', 'barcode']
    success_url = reverse_lazy('inventory:list')

class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'inventory/form.html'
    fields = ['name', 'barcode']
    success_url = reverse_lazy('inventory:list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'inventory/confirm_delete.html'
    success_url = reverse_lazy('inventory:list')