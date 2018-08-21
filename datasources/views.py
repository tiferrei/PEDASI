from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from . import models
from profiles.permissions import OwnerPermissionRequiredMixin


class DataSourceListView(ListView):
    model = models.DataSource
    template_name = 'datasources/datasource/list.html'
    context_object_name = 'datasources'


class DataSourceCreateView(PermissionRequiredMixin, CreateView):
    model = models.DataSource
    fields = '__all__'
    template_name = 'datasources/datasource/create.html'
    context_object_name = 'datasource'

    permission_required = 'datasources.add_datasource'


class DataSourceDetailView(DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/detail.html'
    context_object_name = 'datasource'


class DataSourceUpdateView(OwnerPermissionRequiredMixin, UpdateView):
    model = models.DataSource
    fields = '__all__'
    template_name = 'datasources/datasource/update.html'
    context_object_name = 'datasource'

    permission_required = 'datasources.change_datasource'


class DataSourceDeleteView(OwnerPermissionRequiredMixin, DeleteView):
    model = models.DataSource
    template_name = 'datasources/datasource/delete.html'
    context_object_name = 'datasource'
    success_url = reverse_lazy('datasources:datasource.list')

    permission_required = 'datasources.delete_datasource'


class DataSourceManageAccessView(OwnerPermissionRequiredMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/manage_access.html'
    context_object_name = 'datasource'

    permission_required = 'datasources.change_datasource'
