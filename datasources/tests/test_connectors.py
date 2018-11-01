from django.test import TestCase

from datasources.connectors.base import BaseDataConnector


class ConnectorPluginTest(TestCase):
    def test_load_plugins(self):
        """
        Test that the plugin import process works.
        """
        BaseDataConnector.load_plugins('datasources/connectors')

    def test_get_plugin_iotuk(self):
        """
        Test that we have the IoTUK plugin and can activate it.
        """
        BaseDataConnector.load_plugins('datasources/connectors')
        plugin = BaseDataConnector.get_plugin('IoTUK')

        self.assertIsNotNone(plugin)

    def test_get_plugin_hypercat(self):
        """
        Test that we have the HyperCat plugin and can activate it.
        """
        BaseDataConnector.load_plugins('datasources/connectors')
        plugin = BaseDataConnector.get_plugin('HyperCat')

        self.assertIsNotNone(plugin)

    def test_get_plugin_error(self):
        """
        Test that we cannot activate a plugin which does not exist.
        """
        BaseDataConnector.load_plugins('datasources/connectors')

        with self.assertRaises(KeyError):
            BaseDataConnector.get_plugin('thisplugindoesnotexist')


class ConnectorIoTUKTest(TestCase):
    url = 'https://api.iotuk.org.uk/iotOrganisation'

    def _get_connection(self) -> BaseDataConnector:
        return self.plugin(self.url)

    def setUp(self):
        BaseDataConnector.load_plugins('datasources/connectors')
        self.plugin = BaseDataConnector.get_plugin('DataSetConnector')

    def test_get_plugin(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_init(self):
        connection = self._get_connection()

        self.assertEqual(connection.location, self.url)

    def test_plugin_type(self):
        connection = self._get_connection()

        self.assertFalse(connection.is_catalogue)

    def test_plugin_get_data_fails(self):
        connection = self._get_connection()

        result = connection.get_data()

        self.assertIn('status', result)
        self.assertEqual(result['status'], 400)

        self.assertIn('results', result)
        self.assertEqual(result['results'], -1)

    def test_plugin_get_data_query(self):
        connection = self._get_connection()

        result = connection.get_data(params={'year': 2018})

        self.assertIn('status', result)
        self.assertEqual(result['status'], 200)

        self.assertIn('results', result)
        self.assertGreater(result['results'], 0)

        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)


