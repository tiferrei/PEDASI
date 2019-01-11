from django import forms

from requests.exceptions import ConnectionError

from . import connectors, models


# TODO arrange such that this doesn't need to be loaded each time
connectors.BaseDataConnector.load_plugins('datasources/connectors')


class DataSourceForm(forms.ModelForm):
    """
    Form class for creating / updating DataSource.
    """
    plugin_name = forms.ChoiceField(choices=connectors.BaseDataConnector.plugin_choices,
                                    initial='DataSetConnector')

    class Meta:
        model = models.DataSource
        exclude = ['auth_method', 'owner', 'users']

    def clean(self):
        cleaned_data = super().clean()

        try:
            cleaned_data['auth_method'] = models.DataSource.determine_auth_method(
                cleaned_data['url'],
                cleaned_data['api_key']
            )

        except ConnectionError:
            raise forms.ValidationError('Could not authenticate against URL with provided API key.')

        return cleaned_data

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


class MetadataFieldForm(forms.ModelForm):
    class Meta:
        model = models.MetadataItem
        fields = ['field', 'value']
