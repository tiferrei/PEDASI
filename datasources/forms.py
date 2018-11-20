from django import forms

from . import connectors, models


# TODO arrange such that this doesn't need to be loaded each time
connectors.BaseDataConnector.load_plugins('datasources/connectors')


class DataSourceForm(forms.ModelForm):
    """
    Form class for creating / updating DataSource.
    """
    plugin_name = forms.ChoiceField(choices=connectors.BaseDataConnector.plugin_choices)

    class Meta:
        model = models.DataSource
        exclude = ['owner']

    def clean_encrypted_docs_url(self):
        """
        Make sure that 'is_encrypted' and 'encrypted_docs_url' are always present as a pair.
        """
        if self.cleaned_data['encrypted_docs_url'] and not self.cleaned_data['is_encrypted']:
            raise forms.ValidationError('You may not provide an encryption documentation URL if the data is not encrypted')

        if self.cleaned_data['is_encrypted'] and not self.cleaned_data['encrypted_docs_url']:
            raise forms.ValidationError('You must provide an encryption documentation URL is the data is encrypted')

        return self.cleaned_data['encrypted_docs_url']


class PermissionRequestForm(forms.ModelForm):
    class Meta:
        model = models.UserPermissionLink
        fields = ['requested', 'reason']


class PermissionGrantForm(forms.ModelForm):
    class Meta:
        model = models.UserPermissionLink
        fields = ['granted']
