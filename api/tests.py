import typing

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from datasources import models


class RootApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('Test API User', password='Test API Password')
        cls.token, created = Token.objects.get_or_create(user=cls.user)

    def test_auth_rejected(self):
        """
        Test that we get an authentication failure if not providing a token.
        """
        client = APIClient()

        response = client.get('/api/')

        self.assertEqual(response.status_code, 401)  # 401 Unauthorized

    def test_force_auth(self):
        """
        Test simply that we can access the API using forced authentication.

        This 'authentication' method is used for the API tests.
        """
        client = APIClient()
        client.force_authenticate(self.user)

        response = client.get('/api/')

        self.assertEqual(response.status_code, 200)

    def test_session_auth(self):
        """
        Test simply that we can access the API using session-based authentication.

        This authentication method is used to access the API explorer within the PEDASI UI.
        """
        client = APIClient()
        client.login(username='Test API User', password='Test API Password')

        response = client.get('/api/')

        self.assertEqual(response.status_code, 200)

    def test_token_auth(self):
        """
        Test simply that we can access the API using token based authentication.

        This authentication method is used to access the API from an external application.
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = client.get('/api/')

        self.assertEqual(response.status_code, 200)


class DataSourceApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('Test API User')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.test_name = 'Test DataSource'
        self.test_url = 'https://example.com/test'

    def tearDown(self):
        try:
            self.model.delete()
        except AttributeError:
            pass

    def test_root_api_datasource_exists(self):
        """
        Test that a 'datasources' entry appears in the API root endpoint.
        """
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

        self.assertIn('datasources', response.json().keys())

    def _assert_datasource_correct(self, datasource: typing.Dict):
        """
        Helper function: assert that a :class:`DataSource` received via the API is correct.

        :param datasource: :class:`DataSource` received via API
        """
        self.assertIn('name', datasource)
        self.assertEqual(self.test_name, datasource['name'])

        self.assertIn('description', datasource)
        self.assertEqual('', datasource['description'])

        self.assertIn('url', datasource)
        self.assertEqual(self.test_url, datasource['url'])

    def test_api_datasource_list(self):
        """
        Test the :class:`DataSource` API list functionality.
        """
        response = self.client.get('/api/datasources/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.json()), 0)

        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.user,
            url=self.test_url
        )

        response = self.client.get('/api/datasources/')

        self.assertEqual(len(response.json()), 1)

        datasource = response.json()[0]
        self._assert_datasource_correct(datasource)

    def test_api_datasource_get(self):
        """
        Test the :class:`DataSource` API get one functionality.
        """
        response = self.client.get('/api/datasources/1/')
        self.assertEqual(response.status_code, 404)

        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.user,
            url=self.test_url
        )

        response = self.client.get('/api/datasources/{}/'.format(self.model.pk))
        self.assertEqual(response.status_code, 200)

        datasource = response.json()
        self._assert_datasource_correct(datasource)


class DataSourceApiPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('Test API User')
        cls.owner = get_user_model().objects.create_user('Test API Owner')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.owner_client = APIClient()
        self.owner_client.force_authenticate(self.owner)

        self.test_name = 'Permissions'
        # TODO don't rely on external URL for testing
        self.test_url = 'https://api.iotuk.org.uk/iotOrganisation'

    def tearDown(self):
        try:
            self.model.delete()
        except AttributeError:
            pass

    def _grant_permission(self, level: models.UserPermissionLevels):
        response = self.owner_client.post('/datasources/{}/access/grant'.format(self.model.pk),
                                          data={
                                              'user': self.user.pk,
                                              'granted': level.value,
                                          },
                                          headers={
                                              'Accept': 'application/json'
                                          })
        # TODO make this return a proper response code for AJAX-like requests
        self.assertEqual(response.status_code, 302)

    def test_datasource_permission_view(self):
        """
        Test that permissions are correctly handled when attempting to view a data source.
        """
        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.owner,
            url=self.test_url,
            plugin_name='DataSetConnector',
            access_control=True
        )

        url = '/api/datasources/{}/'.format(self.model.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.VIEW)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self._grant_permission(models.UserPermissionLevels.META)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self._grant_permission(models.UserPermissionLevels.DATA)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self._grant_permission(models.UserPermissionLevels.PROV)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_datasource_permission_meta(self):
        """
        Test that permissions are correctly handled when attempting to get metadata from a data source.
        """
        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.owner,
            url=self.test_url,
            plugin_name='DataSetConnector',
            access_control=True
        )

        url = '/api/datasources/{}/metadata/'.format(self.model.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.VIEW)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.META)

        response = self.client.get(url)
        # This data connector does not provide metadata
        self.assertEqual(response.status_code, 400)

        self._grant_permission(models.UserPermissionLevels.DATA)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        self._grant_permission(models.UserPermissionLevels.PROV)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_datasource_permission_data(self):
        """
        Test that permissions are correctly handled when attempting to get data from a data source.
        """
        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.owner,
            url=self.test_url,
            plugin_name='DataSetConnector',
            access_control=True
        )

        url = '/api/datasources/{}/data/?year=2018'.format(self.model.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.VIEW)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.META)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.DATA)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self._grant_permission(models.UserPermissionLevels.PROV)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_datasource_permission_prov(self):
        """
        Test that permissions are correctly handled when attempting to get PROV data from a data source.
        """
        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.owner,
            url=self.test_url,
            plugin_name='DataSetConnector',
            access_control=True
        )

        url = '/api/datasources/{}/prov/'.format(self.model.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.VIEW)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.META)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.DATA)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._grant_permission(models.UserPermissionLevels.PROV)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class DataSourceApiIoTUKTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('Test API User')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.test_name = 'IoTUK'
        self.test_url = 'https://api.iotuk.org.uk/iotOrganisation'

    def tearDown(self):
        try:
            self.model.delete()
        except AttributeError:
            pass

    def test_api_datasource_get(self):
        """
        Test the :class:`DataSource` API get one functionality.
        """
        response = self.client.get('/api/datasources/1/')
        self.assertEqual(response.status_code, 404)

        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.user,
            url=self.test_url,
            plugin_name='DataSetConnector'
        )

        response = self.client.get('/api/datasources/{}/'.format(self.model.pk))
        self.assertEqual(response.status_code, 200)

        datasource = response.json()

        self.assertIn('name', datasource)
        self.assertEqual(self.test_name, datasource['name'])

        self.assertIn('description', datasource)
        self.assertEqual('', datasource['description'])

        self.assertIn('url', datasource)
        self.assertEqual(self.test_url, datasource['url'])

    def test_api_datasource_get_data(self):
        """
        Test the :class:`DataSource` API functionality to retrieve data.
        """
        response = self.client.get('/api/datasources/1/data/')
        self.assertEqual(response.status_code, 404)

        self.model = models.DataSource.objects.create(
            name=self.test_name,
            owner=self.user,
            url=self.test_url,
            plugin_name='DataSetConnector'
        )

        response = self.client.get('/api/datasources/{}/data/'.format(self.model.pk))
        # Query should fail since IoTUK requires query filters
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/datasources/{}/data/?year=2017'.format(self.model.pk))
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn('results', data)
        self.assertLessEqual(1, data['results'])
        self.assertIn('data', data)
        self.assertLessEqual(1, len(data['data']))


class DataSourceApiHyperCatTest(TestCase):
    test_name = 'HyperCat'
    plugin_name = 'HyperCat'
    test_url = 'https://api.cityverve.org.uk/v1/cat/polling-station'
    dataset = 'https://api.cityverve.org.uk/v1/entity/polling-station/5'

    @classmethod
    def setUpTestData(cls):
        from decouple import config

        cls.user = get_user_model().objects.create_user('Test API User')

        cls.api_key = config('HYPERCAT_CISCO_API_KEY')

        cls.model = models.DataSource.objects.create(
            name=cls.test_name,
            owner=cls.user,
            url=cls.test_url,
            api_key=cls.api_key,
            plugin_name=cls.plugin_name
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_api_datasource_get(self):
        """
        Test the :class:`DataSource` API get one functionality.
        """
        response = self.client.get('/api/datasources/{}/'.format(self.model.pk))
        self.assertEqual(response.status_code, 200)

        datasource = response.json()

        self.assertIn('name', datasource)
        self.assertEqual(self.test_name, datasource['name'])

        self.assertIn('description', datasource)
        self.assertEqual('', datasource['description'])

        self.assertIn('url', datasource)
        self.assertEqual(self.test_url, datasource['url'])

    def test_api_datasource_get_metadata(self):
        """
        Test the :class:`DataSource` API functionality to retrieve metadata.
        """
        response = self.client.get('/api/datasources/{}/metadata/'.format(self.model.pk))
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn('status', data)
        self.assertEqual('success', data['status'])
        self.assertIn('data', data)
        self.assertLessEqual(1, len(data['data']))
        # TODO test contents of 'data' list

    def test_api_datasource_get_datasets(self):
        """
        Test the :class:`DataSource` API functionality to retrieve the list of datasets.
        """
        response = self.client.get('/api/datasources/{}/datasets/'.format(self.model.pk))
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn('status', data)
        self.assertEqual('success', data['status'])
        self.assertIn('data', data)
        self.assertLessEqual(1, len(data['data']))
        # TODO test contents of 'data' list

    def test_api_datasource_get_dataset_metadata(self):
        """
        Test the :class:`DataSource` API functionality to retrieve dataset metadata.
        """
        response = self.client.get('/api/datasources/{}/datasets/{}/metadata/'.format(self.model.pk, self.dataset))
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn('status', data)
        self.assertEqual('success', data['status'])
        self.assertIn('data', data)
        self.assertLessEqual(1, len(data['data']))
        # TODO test contents of 'data' list

    def test_api_datasource_get_dataset_data(self):
        """
        Test the :class:`DataSource` API functionality to retrieve dataset data.
        """
        response = self.client.get('/api/datasources/{}/datasets/{}/data/'.format(self.model.pk, self.dataset))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data)
        # TODO test content


if __name__ == '__main__':
    TestCase.run()
