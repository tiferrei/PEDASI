from django.views.generic.detail import DetailView

from profiles import models


class InstitutionDetailView(DetailView):
    model = models.Institution
    template_name = 'profiles/institution/detail.html'
    context_object_name = 'institution'
