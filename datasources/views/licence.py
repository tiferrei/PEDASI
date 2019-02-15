from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .. import forms, models
from profiles.permissions import OwnerPermissionMixin


class LicenceListView(ListView):
    model = models.Licence
    template_name = 'datasources/licence/list.html'
    context_object_name = 'licences'


class LicenceCreateView(PermissionRequiredMixin, CreateView):
    model = models.Licence
    template_name = 'datasources/licence/create.html'
    context_object_name = 'licence'

    form_class = forms.LicenceForm
    permission_required = 'datasources.add_licence'

    def form_valid(self, form):
        try:
            owner = form.instance.owner

        except models.Licence.owner.RelatedObjectDoesNotExist:
            form.instance.owner = self.request.user

        return super().form_valid(form)


class LicenceDetailView(DetailView):
    model = models.Licence
    template_name = 'datasources/licence/detail.html'
    context_object_name = 'licence'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['has_edit_permission'] = self.request.user.is_superuser or self.request.user == self.object.owner

        return context


class LicenceUpdateView(OwnerPermissionMixin, UpdateView):
    model = models.Licence
    template_name = 'datasources/licence/update.html'
    context_object_name = 'licence'

    form_class = forms.LicenceForm

    def form_valid(self, form):
        try:
            owner = form.instance.owner

        except models.Licence.owner.RelatedObjectDoesNotExist:
            form.instance.owner = self.request.user

        return super().form_valid(form)


class LicenceDeleteView(OwnerPermissionMixin, DeleteView):
    model = models.Licence
    template_name = 'datasources/licence/delete.html'
    context_object_name = 'licence'

    success_url = reverse_lazy('datasources:licence.list')
