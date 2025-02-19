from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Visit, MachineRefill
from machines.models import Location, VendingMachine
from inventory.models import Product

class VisitListView(LoginRequiredMixin, ListView):
    model = Visit
    template_name = 'visits/list.html'
    context_object_name = 'visits'
    login_url = '/login/'  # Redirect to login if not authenticated

class VisitDetailView(LoginRequiredMixin, DetailView):
    model = Visit
    template_name = 'visits/detail.html'
    login_url = '/login/'  # Redirect to login if not authenticated

class VisitCreateView(LoginRequiredMixin, CreateView):
    model = Visit
    template_name = 'visits/form.html'
    fields = ['location', 'date_visited', 'notes']
    success_url = reverse_lazy('visits:list')
    login_url = '/login/'  # Redirect to login if not authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['machines'] = VendingMachine.objects.all()
        context['products'] = Product.objects.all()
        return context

    def form_valid(self, form):
        visit = form.save()
        machines = self.request.POST.getlist('machines')
        products = self.request.POST.getlist('products')
        units_added = self.request.POST.getlist('units_added')

        for machine_id, product_id, units in zip(machines, products, units_added):
            machine = VendingMachine.objects.get(id=machine_id)
            product = Product.objects.get(id=product_id)
            MachineRefill.objects.create(
                visit=visit,
                vending_machine=machine,
                product=product,
                units_added=units
            )

        return super().form_valid(form)

class VisitUpdateView(LoginRequiredMixin, UpdateView):
    model = Visit
    template_name = 'visits/form.html'
    fields = ['vending_machine', 'notes']
    success_url = reverse_lazy('visits:list')
    login_url = '/login/'  # Redirect to login if not authenticated

class VisitDeleteView(LoginRequiredMixin, DeleteView):
    model = Visit
    template_name = 'visits/confirm_delete.html'
    success_url = reverse_lazy('visits:list')
    login_url = '/login/'  # Redirect to login if not authenticated