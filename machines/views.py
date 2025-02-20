from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Location, VendingMachine

# Location Views
class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'machines/location_list.html'
    context_object_name = 'locations'
    login_url = '/login/'

class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    template_name = 'machines/location_form.html'
    fields = ['name', 'address_1', 'address_2', 'city', 'state', 'zip_code']
    success_url = reverse_lazy('machines:location_list')
    login_url = '/login/'

class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    template_name = 'machines/location_form.html'
    fields = ['name', 'address_1', 'address_2', 'city', 'state', 'zip_code']
    success_url = reverse_lazy('machines:location_list')
    login_url = '/login/'

class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = 'machines/location_confirm_delete.html'
    success_url = reverse_lazy('machines:location_list')
    login_url = '/login/'

# VendingMachine Views
class VendingMachineListView(LoginRequiredMixin, ListView):
    model = VendingMachine
    template_name = 'machines/list.html'
    context_object_name = 'machines'
    login_url = '/login/'  # Redirect to login if not authenticated

class VendingMachineDetailView(LoginRequiredMixin, DetailView):
    model = VendingMachine
    template_name = 'machines/detail.html'
    login_url = '/login/'  # Redirect to login if not authenticated

class VendingMachineCreateView(LoginRequiredMixin, CreateView):
    model = VendingMachine
    template_name = 'machines/form.html'
    fields = ['name', 'location']
    success_url = reverse_lazy('machines:list')
    login_url = '/login/'  # Redirect to login if not authenticated

class VendingMachineUpdateView(LoginRequiredMixin, UpdateView):
    model = VendingMachine
    template_name = 'machines/form.html'
    fields = ['name', 'location']
    success_url = reverse_lazy('machines:list')
    login_url = '/login/'  # Redirect to login if not authenticated

class VendingMachineDeleteView(LoginRequiredMixin, DeleteView):
    model = VendingMachine
    template_name = 'machines/confirm_delete.html'
    success_url = reverse_lazy('machines:list')
    login_url = '/login/'  # Redirect to login if not authenticated