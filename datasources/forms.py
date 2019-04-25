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
            # TODO construct and actual data connector instance here
            cleaned_data['auth_method'] = connectors.BaseDataConnector.determine_auth_method(
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
        fields = ['user', 'requested', 'push_requested', 'reason']
        widgets = {
            'reason': forms.Textarea
        }
        help_texts = {
            'user': 'You may request permission for yourself or on behalf of any applications for which you are responsible.',
            'push_requested': 'Do you also require permission to push data?',
        }

    def __init__(self, *args, **kwargs):
        user_choices = kwargs.pop('user_choices')
        user_initial = kwargs.pop('user_initial')
        user_field_hidden = kwargs.pop('user_field_hidden')

        super().__init__(*args, **kwargs)

        self.fields['user'].choices = user_choices
        self.fields['user'].initial = user_initial

        if user_field_hidden:
            self.fields['user'].widget = forms.HiddenInput()

    def save(self, commit=True):
        """
        Save this permission request.

        Because (user, datasource) are unique, if the user is changed we need to get the corresponding record.
        """
        record, created = models.UserPermissionLink.objects.get_or_create(
            user=self.instance.user,
            datasource=self.instance.datasource
        )

        record.requested = self.instance.requested
        record.push_requested = self.instance.push_requested
        record.reason = self.instance.reason

        record.save()


class PermissionGrantForm(forms.ModelForm):
    class Meta:
        model = models.UserPermissionLink
        fields = ['granted', 'push_granted']


class LicenceForm(forms.ModelForm):
    class Meta:
        model = models.Licence
        exclude = ['owner']
