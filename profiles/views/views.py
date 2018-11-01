from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from applications.models import Application
from datasources.models import DataSource


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Add recent Applications and DataSources to index page.

        :return: Django context dictionary
        """
        context = super().get_context_data(**kwargs)

        context['datasources'] = DataSource.objects.order_by('-id')[:3]
        context['applications'] = Application.objects.order_by('-id')[:3]

        return context


class UserProfileView(DetailView):
    template_name = 'profiles/user/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


class UserInactiveView(TemplateView):
    template_name = 'profiles/user/inactive.html'
