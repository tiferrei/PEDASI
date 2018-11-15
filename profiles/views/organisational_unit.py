from django.views.generic.detail import DetailView

from profiles import models


class OrganisationalUnitDetailView(DetailView):
    model = models.OrganisationalUnit
    template_name = 'profiles/organisational_unit/detail.html'
    context_object_name = 'organisational_unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['datasources'] = []
        for user in self.object.users.all():
            context['datasources'].extend(user.datasources.all())

        return context
