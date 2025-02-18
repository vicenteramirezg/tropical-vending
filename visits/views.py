from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Visit

class VisitListView(ListView):
    model = Visit
    template_name = 'visits/list.html'
    context_object_name = 'visits'

class VisitDetailView(DetailView):
    model = Visit
    template_name = 'visits/detail.html'

class VisitCreateView(CreateView):
    model = Visit
    template_name = 'visits/form.html'
    fields = ['vending_machine', 'notes']
    success_url = reverse_lazy('visits:list')

class VisitUpdateView(UpdateView):
    model = Visit
    template_name = 'visits/form.html'
    fields = ['vending_machine', 'notes']
    success_url = reverse_lazy('visits:list')

class VisitDeleteView(DeleteView):
    model = Visit
    template_name = 'visits/confirm_delete.html'
    success_url = reverse_lazy('visits:list')