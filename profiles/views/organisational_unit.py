from django.views.generic.detail import DetailView

from profiles import models


class OrganisationalUnitDetailView(DetailView):
    model = models.OrganisationalUnit
    template_name = 'profiles/organisational_unit/detail.html'
    context_object_name = 'organisational_unit'
