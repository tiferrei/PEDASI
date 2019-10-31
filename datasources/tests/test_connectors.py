from django.test import TestCase

from datasources.connectors.base import AuthMethod, BaseDataConnector


class ConnectorPluginTest(TestCase):
    def test_load_plugins(self):
        """
        Test that the plugin import process works.
        """
        BaseDataConnector.load_plugins('datasources/connectors')

    def test_get_plugin_simple(self):
        """
        Test that we have the plugin for trivial APIs and can activate it.
        """
        BaseDataConnector.load_plugins('datasources/connectors')
        plugin = BaseDataConnector.get_plugin('DataSetConnector')

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


class ConnectorBaseTest(TestCase):
    url = 'https://api.github.com/repos/PEDASI/PEDASI/issues'

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

    def test_plugin_get_data(self):
        connection = self._get_connection()

        result = connection.get_data()

        self.assertTrue(len(result))

        first_issue = result[0]
        self.assertIn('url', first_issue)
        self.assertTrue(first_issue['url'].startswith(self.url))

    def test_plugin_get_data_query(self):
        connection = self._get_connection()

        # Get all closed issues from PEDASI repo
        closed_issues = connection.get_data(params={'state': 'closed'})

        self.assertTrue(len(closed_issues))

        first_closed_issue = closed_issues[0]
        self.assertIn('state', first_closed_issue)
        self.assertEqual(first_closed_issue['state'], 'closed')

        self.assertIn(first_closed_issue, closed_issues)

        # Get all open issues from PEDASI repo
        open_issues = connection.get_data(params={'state': 'open'})

        if open_issues:
            first_open_issue = open_issues[0]
            self.assertIn('state', first_open_issue)
            self.assertEqual(first_open_issue['state'], 'open')

        self.assertNotIn(first_closed_issue, open_issues)


    def test_determine_auth(self):
        connection = self._get_connection()

        auth_method = connection.determine_auth_method(connection.location, connection.api_key)

        self.assertEqual(AuthMethod.NONE, auth_method)


class ConnectorRestApiTest(TestCase):
    url = 'https://api.github.com/repos/PEDASI/PEDASI'

    def _get_connection(self) -> BaseDataConnector:
        return self.plugin(self.url)

    def setUp(self):
        BaseDataConnector.load_plugins('datasources/connectors')
        self.plugin = BaseDataConnector.get_plugin('RestApiConnector')

    def test_get_plugin(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_init(self):
        connection = self._get_connection()

        self.assertEqual(connection.location, self.url)

    def test_plugin_type(self):
        connection = self._get_connection()

        self.assertTrue(connection.is_catalogue)

    def test_plugin_get_data(self):
        connection = self._get_connection()

        result = connection.get_data()

        self.assertIn('name', result)
        self.assertEqual('PEDASI', result['name'])


    def test_plugin_dataset_get_data_query(self):
        connection = self._get_connection()

        closed_issues = connection['issues'].get_data(params={'state': 'closed'})
        
        import pprint
        pprint.pprint(closed_issues)

        self.assertTrue(len(closed_issues))

        first_closed_issue = closed_issues[0]
        self.assertIn('state', first_closed_issue)
        self.assertEqual(first_closed_issue['state'], 'closed')

        self.assertIn(first_closed_issue, closed_issues)