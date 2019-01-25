from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from profiles.permissions import OwnerPermissionRequiredMixin
from datasources import forms, models


class DataSourceAccessManageView(OwnerPermissionRequiredMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/manage_access.html'
    context_object_name = 'datasource'

    permission_required = 'datasources.change_datasource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_users'] = get_user_model().objects

        context['permissions_requested'] = models.UserPermissionLink.objects.filter(
            datasource=self.object,
            requested__gt=F('granted')
        ).union(
            models.UserPermissionLink.objects.filter(
                datasource=self.object,
            ).exclude(
                push_requested=F('push_granted')
            )
        )

        context['permissions_granted'] = models.UserPermissionLink.objects.filter(
            datasource=self.object,
            requested__lte=F('granted'),
            push_requested=F('push_granted')
        )

        return context


# TODO check permissions
class DataSourceAccessGrantView(LoginRequiredMixin, UpdateView):
    """
    Manage a user's access to a DataSource.

    Provides a form view to edit permissions, but permissions may also be set using an AJAX POST request.
    """
    model = models.UserPermissionLink
    form_class = forms.PermissionGrantForm
    context_object_name = 'permission'
    template_name = 'datasources/user_permission_link/permission_grant.html'

    def get_context_data(self, **kwargs):
        """
        Add data source to the context.
        """
        context = super().get_context_data()

        context['datasource'] = models.DataSource.objects.get(pk=self.kwargs['pk'])

        return context

    def get_object(self, queryset=None):
        """
        Get or create a permission object for the relevant user.
        """
        self.datasource = models.DataSource.objects.get(pk=self.kwargs['pk'])

        try:
            user = get_user_model().objects.get(id=self.request.POST.get('user'))

        except get_user_model().DoesNotExist:
            user = get_user_model().objects.get(id=self.request.GET.get('user'))

        obj, created = self.model.objects.get_or_create(
            user=user,
            datasource=self.datasource
        )

        # Set default value to approve request - but do not automatically save this
        obj.granted = obj.requested
        obj.push_granted = obj.push_requested

        return obj

    def form_valid(self, form):
        """
        Automatically grant requests which are either:
            - Edited by owner / admin
            - Requests for a reduction in permission level
        """
        form.instance.requested = form.instance.granted
        form.instance.push_requested = form.instance.push_granted

        if form.instance.requested == models.UserPermissionLevels.NONE and not form.instance.push_requested:
            form.instance.delete()

        else:
            form.instance.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        Return to access management view.
        """
        return reverse('datasources:datasource.access.manage', kwargs={'pk': self.datasource.pk})


class DataSourceAccessRequestView(LoginRequiredMixin, UpdateView):
    """
    Request access to a data source, or request changes to an existing permission.

    Provides a form view to edit permission requests, but permissions may also be requested using an AJAX POST request.
    """
    model = models.UserPermissionLink
    form_class = forms.PermissionRequestForm
    template_name = 'datasources/user_permission_link/permission_request.html'

    def get_context_data(self, **kwargs):
        """
        Add data source to the context.
        """
        context = super().get_context_data()

        context['datasource'] = models.DataSource.objects.get(pk=self.kwargs['pk'])

        return context

    def get_object(self, queryset=None):
        """
        Get or create a permission object for the relevant user.
        """
        self.datasource = models.DataSource.objects.get(pk=self.kwargs['pk'])
        user = self.request.user

        if self.request.user == self.datasource.owner or self.request.user.is_superuser:
            try:
                # Let owner and admins edit other user's requests
                user = get_user_model().objects.get(id=self.request.GET.get('user'))

            except ObjectDoesNotExist:
                pass

        try:
            # Is there an existing record?
            obj = self.model.objects.get(
                user=user,
                datasource=self.datasource
            )

        except self.model.DoesNotExist:
            # Don't save to DB - only temporary
            obj = self.model(
                user=user,
                datasource=self.datasource
            )

        return obj

    def get_form(self, form_class=None):
        """
        Get form with choices and default value set for user field.
        """
        # Authenticated user and any applications for which they are responsible
        user_choices = [(self.request.user.pk, self.request.user.username)]
        user_choices += [(app.proxy_user.pk, 'App: ' + app.name) for app in self.request.user.applications.all()]

        user_field_hidden = len(user_choices) <= 1

        if form_class is None:
            form_class = self.get_form_class()

        return form_class(
            user_choices=user_choices,
            user_initial=self.request.user,
            user_field_hidden=user_field_hidden,
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        """
        Automatically grant requests which are either:
            - Edited by owner / admin
            - Requests for a reduction in permission level
        """
        if form.instance.requested == models.UserPermissionLevels.NONE:
            form.instance.delete()

        else:
            if (
                    (self.request.user == self.datasource.owner or self.request.user.is_superuser) or
                    form.instance.granted > form.instance.requested
            ):
                form.instance.granted = form.instance.requested

            form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        Return to the data source or access management view depending on user class.
        """
        if self.request.user == self.datasource.owner or self.request.user.is_superuser:
            return reverse('datasources:datasource.access.manage', kwargs={'pk': self.datasource.pk})

        return reverse('datasources:datasource.detail', kwargs={'pk': self.datasource.pk})


