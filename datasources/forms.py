from django import forms

from . import models


class PermissionRequestForm(forms.ModelForm):
    class Meta:
        model = models.UserPermissionLink
        fields = ['requested', 'reason']


class PermissionGrantForm(forms.ModelForm):
    class Meta:
        model = models.UserPermissionLink
        fields = ['user', 'requested', 'reason', 'granted']
