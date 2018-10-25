import typing

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from datasources import models


class RootApiTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_api(self):
        """
        Test simply that we can access the API root.

        This endpoint lists the available API components.
        """
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)


class DataSourceApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            'Test User', 'test@example.com', 'testpassword'
        )

    def setUp(self):
        self.client = Client()

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

        response = self.client.get('/api/datasources/1/')
        self.assertEqual(response.status_code, 200)

        datasource = response.json()
        self._assert_datasource_correct(datasource)


class DataSourceApiIoTUKTest(DataSourceApiTest):
    def setUp(self):
        self.client = Client()

        self.test_name = 'IoTUK'
        self.test_url = 'https://api.iotuk.org.uk/iotOrganisation'

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
            plugin_name='IoTUK'
        )

        response = self.client.get('/api/datasources/1/')
        self.assertEqual(response.status_code, 200)

        datasource = response.json()
        self._assert_datasource_correct(datasource)

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
            plugin_name='IoTUK'
        )

        response = self.client.get('/api/datasources/1/data/')
        # Query should fail since IoTUK requires query filters
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/datasources/1/data/?year=2017')
        self.assertEqual(response.status_code, 200)

        datasource = response.json()
        self._assert_datasource_correct(datasource)
