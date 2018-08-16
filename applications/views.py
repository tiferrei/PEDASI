from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from . import models
from profiles.permissions import OwnerPermissionRequiredMixin


class ApplicationListView(ListView):
    model = models.Application
    template_name = 'applications/application/list.html'
    context_object_name = 'applications'


class ApplicationCreateView(PermissionRequiredMixin, CreateView):
    model = models.Application
    fields = '__all__'
    template_name = 'applications/application/create.html'
    context_object_name = 'application'

    permission_required = 'applications.add_application'


class ApplicationDetailView(DetailView):
    model = models.Application
    template_name = 'applications/application/detail.html'
    context_object_name = 'application'


class ApplicationUpdateView(OwnerPermissionRequiredMixin, UpdateView):
    model = models.Application
    fields = '__all__'
    template_name = 'applications/application/update.html'
    context_object_name = 'application'

    permission_required = 'applications.change_application'


class ApplicationDeleteView(OwnerPermissionRequiredMixin, DeleteView):
    model = models.Application
    template_name = 'applications/application/delete.html'
    context_object_name = 'application'
    success_url = reverse_lazy('applications:application.list')

    permission_required = 'applications.delete_application'
