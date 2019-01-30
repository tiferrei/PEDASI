from django.views.generic import CreateView, DetailView, ListView

from .. import models


class LicenceListView(ListView):
    model = models.License
    template_name = 'datasources/licence/list.html'
    context_object_name = 'licences'


class LicenceCreateView(CreateView):
    model = models.License
    template_name = 'datasources/licence/create.html'
    context_object_name = 'licence'

    fields = '__all__'


class LicenceDetailView(DetailView):
    model = models.License
    template_name = 'datasources/licence/detail.html'
    context_object_name = 'licence'
