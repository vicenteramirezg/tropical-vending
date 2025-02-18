from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import VendingMachine

class VendingMachineListView(ListView):
    model = VendingMachine
    template_name = 'machines/list.html'
    context_object_name = 'machines'

class VendingMachineDetailView(DetailView):
    model = VendingMachine
    template_name = 'machines/detail.html'

class VendingMachineCreateView(CreateView):
    model = VendingMachine
    template_name = 'machines/form.html'
    fields = ['name', 'location']
    success_url = reverse_lazy('machines:list')

class VendingMachineUpdateView(UpdateView):
    model = VendingMachine
    template_name = 'machines/form.html'
    fields = ['name', 'location']
    success_url = reverse_lazy('machines:list')

class VendingMachineDeleteView(DeleteView):
    model = VendingMachine
    template_name = 'machines/confirm_delete.html'
    success_url = reverse_lazy('machines:list')