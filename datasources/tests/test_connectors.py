import typing

from django.test import TestCase

from datasources.connectors.base import BaseDataConnector


def _get_item_by_key_value(collection: typing.Iterable[typing.Mapping],
                           key: str, value) -> typing.Mapping:
    matches = [item for item in collection if item[key] == value]

    if not matches:
        raise KeyError
    elif len(matches) > 1:
        raise ValueError('Multiple items were found')

    return matches[0]


def _count_items_by_key_value(collection: typing.Iterable[typing.Mapping],
                              key: str, value) -> int:
    matches = [item for item in collection if item[key] == value]

    return len(matches)


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
        result = connection.get_data(params={'year': 2018})

        self.assertIn('status', result)
        self.assertEqual(result['status'], 200)

        self.assertIn('results', result)
        self.assertGreater(result['results'], 0)

        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)


class ConnectorHyperCatTest(TestCase):
    url = 'https://portal.bt-hypercat.com/cat'

    # Met Office dataset for weather at Heathrow
    dataset = 'http://api.bt-hypercat.com/sensors/feeds/c7f361c6-7cb7-4ef5-aed9-397a0c0c4088'

    def setUp(self):
        BaseDataConnector.load_plugins('datasources/connectors')
        self.plugin = BaseDataConnector.get_plugin('HyperCat')

    def test_get_plugin(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_init(self):
        connection = self.plugin(self.url)
        self.assertEqual(connection.location, self.url)

    def test_plugin_get_metadata(self):
        connection = self.plugin(self.url)
        result = connection.get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-hypercat:rels:hasDescription:en',
            'urn:X-hypercat:rels:isContentType',
        ]:
            self.assertIn(property, relations)

        self.assertEqual('BT Hypercat DataHub Catalog',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasDescription:en')['val'])

        self.assertEqual('application/vnd.hypercat.catalogue+json',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:isContentType')['val'])

    def test_plugin_get_dataset_metadata(self):
        connection = self.plugin(self.url)
        result = connection[self.dataset].get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-bt:rels:feedTitle',
            'urn:X-hypercat:rels:hasDescription:en',
            'urn:X-bt:rels:feedTag',
            'urn:X-bt:rels:hasSensorStream',
            'urn:X-hypercat:rels:isContentType',
        ]:
            self.assertIn(property, relations)

        self.assertIn('Met Office',
                      _get_item_by_key_value(result, 'rel', 'urn:X-bt:rels:feedTitle')['val'])

        self.assertIn('Met Office',
                      _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasDescription:en')['val'])

        self.assertEqual(1,
                         _count_items_by_key_value(result, 'rel', 'urn:X-bt:rels:feedTag'))
        # self.assertEqual(result['urn:X-bt:rels:feedTag'][0], 'weather')

        self.assertGreaterEqual(_count_items_by_key_value(result, 'rel', 'urn:X-bt:rels:hasSensorStream'),
                                1)

        # self.assertIn('application/json',
        #               result['urn:X-hypercat:rels:isContentType'])

    def test_plugin_get_dataset_data(self):
        """
        Test that we can get data from a single dataset within the catalogue.
        """
        from decouple import config

        api_key = config('HYPERCAT_BT_API_KEY')

        connection = self.plugin(self.url,
                                 api_key=api_key)
        # result = connection[self.dataset + '/datastreams/0'].get_data()
        result = connection[self.dataset].get_data()

        self.assertIsInstance(result, str)
        self.assertGreaterEqual(len(result), 1)
        self.assertIn('c7f361c6-7cb7-4ef5-aed9-397a0c0c4088',
                      result)


class ConnectorHyperCatCiscoTest(TestCase):
    url = 'https://api.cityverve.org.uk/v1/cat'
    entity_url = 'https://api.cityverve.org.uk/v1/entity'

    dataset = 'weather-observations-wind'

    def setUp(self):
        from decouple import config

        BaseDataConnector.load_plugins('datasources/connectors')
        self.plugin = BaseDataConnector.get_plugin('HyperCatCisco')

        self.api_key = config('HYPERCAT_CISCO_API_KEY')

    def test_get_plugin(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_init(self):
        connection = self.plugin(self.url)
        self.assertEqual(connection.location, self.url)

    def test_plugin_get_entities(self):
        connection = self.plugin(self.url,
                                 api_key=self.api_key,
                                 entity_url=self.entity_url)
        result = connection.get_entities()

        self.assertGreaterEqual(len(result), 1)

        for entity in result:
            self.assertIn('id', entity)
            self.assertIn('uri', entity)

    def test_plugin_get_catalogue_metadata(self):
        connection = self.plugin(self.url,
                                 api_key=self.api_key)
        result = connection.get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-hypercat:rels:hasDescription:en',
            'urn:X-hypercat:rels:isContentType',
            'urn:X-hypercat:rels:hasHomepage',
        ]:
            self.assertIn(property, relations)

        self.assertEqual('CityVerve Public API - master catalogue',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasDescription:en')['val'])

        self.assertEqual('application/vnd.hypercat.catalogue+json',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:isContentType')['val'])

        self.assertEqual('https://developer.cityverve.org.uk',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasHomepage')['val'])

    def test_plugin_get_subcatalogue_metadata(self):
        connection = self.plugin(self.url)
        result = connection[self.dataset].get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-hypercat:rels:hasDescription:en',
            'urn:X-hypercat:rels:isContentType',
            'urn:X-hypercat:rels:hasHomepage',
        ]:
            self.assertIn(property, relations)

        self.assertEqual('CityVerve Public API - master catalogue',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasDescription:en')['val'])

        self.assertEqual('application/vnd.hypercat.catalogue+json',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:isContentType')['val'])

        self.assertEqual('https://developer.cityverve.org.uk',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasHomepage')['val'])

    def test_plugin_get_dataset_metadata(self):
        connection = self.plugin(self.url)
        result = connection[self.dataset].get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-bt:rels:feedTitle',
            'urn:X-hypercat:rels:hasDescription:en',
            'urn:X-bt:rels:feedTag',
            'urn:X-bt:rels:hasSensorStream',
            'urn:X-hypercat:rels:isContentType',
        ]:
            self.assertIn(property, relations)

        self.assertIn('Met Office',
                      _get_item_by_key_value(result, 'rel', 'urn:X-bt:rels:feedTitle')['val'])

        self.assertIn('Met Office',
                      _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasDescription:en')['val'])

        self.assertEqual(1,
                         _count_items_by_key_value(result, 'rel', 'urn:X-bt:rels:feedTag'))
        # self.assertEqual(result['urn:X-bt:rels:feedTag'][0], 'weather')

        self.assertGreaterEqual(_count_items_by_key_value(result, 'rel', 'urn:X-bt:rels:hasSensorStream'),
                                1)

        # self.assertIn('application/json',
        #               result['urn:X-hypercat:rels:isContentType'])

