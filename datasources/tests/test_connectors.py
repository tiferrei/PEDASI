from django.test import TestCase

from datasources.connectors.base import BaseDataConnector


class ConnectorPluginTest(TestCase):
    def test_load_plugins(self):
        BaseDataConnector.load_plugins('datasources/connectors')


class ConnectorIoTUKTest(TestCase):
    url = 'https://api.iotuk.org.uk/iotOrganisation'

    def setUp(self):
        BaseDataConnector.load_plugins('datasources/connectors')
        self.plugin = BaseDataConnector.get_plugin('IoTUK')

    def test_get_plugin(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_init(self):
        connection = self.plugin(self.url)
        self.assertEqual(connection.location, self.url)

    def test_plugin_get_data_fails(self):
        connection = self.plugin(self.url)
        result = connection.get_data()

        self.assertIn('status', result)
        self.assertEqual(result['status'], 400)

        self.assertIn('results', result)
        self.assertEqual(result['results'], -1)

    def test_plugin_get_data_query(self):
        connection = self.plugin(self.url)
        result = connection.get_data(query_params={'year': 2018})

        self.assertIn('status', result)
        self.assertEqual(result['status'], 200)

        self.assertIn('results', result)
        self.assertGreater(result['results'], 0)

        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
