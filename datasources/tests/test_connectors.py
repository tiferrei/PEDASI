import itertools
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
        from decouple import config

        BaseDataConnector.load_plugins('datasources/connectors')
        self.plugin = BaseDataConnector.get_plugin('HyperCat')

        self.api_key = config('HYPERCAT_BT_API_KEY')

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

    def test_plugin_get_datasets(self):
        connection = self.plugin(self.url)
        datasets = connection.get_datasets()

        self.assertEqual(list,
                         type(datasets))

        self.assertLessEqual(1,
                             len(datasets))

        self.assertIn(self.dataset,
                      datasets)

    def test_plugin_iter_datasets(self):
        connection = self.plugin(self.url)

        for dataset in connection:
            self.assertEqual(str,
                             type(dataset))

    def test_plugin_len_datasets(self):
        connection = self.plugin(self.url)

        self.assertLessEqual(1,
                             len(connection))

    def test_plugin_iter_items(self):
        """
        Test naive iteration over key-value pairs of datasets within this catalogue.

        This process is SLOW so we only do a couple of iterations.
        """
        connection = self.plugin(self.url,
                                 api_key=self.api_key)

        for k, v in itertools.islice(connection.items(), 5):
            self.assertEqual(str,
                             type(k))

            self.assertIsInstance(v,
                                  BaseDataConnector)

            self.assertEqual(k,
                             v.location)

    def test_plugin_iter_items_context_manager(self):
        """
        Test context-managed iteration over key-value pairs of datasets within this catalogue.

        This process is relatively slow so we only do a couple of iterations.
        """
        with self.plugin(self.url, api_key=self.api_key) as connection:
            for k, v in itertools.islice(connection.items(), 5):
                self.assertEqual(str,
                                 type(k))

                self.assertIsInstance(v,
                                      BaseDataConnector)

                self.assertEqual(k,
                                 v.location)

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

        self.assertGreaterEqual(_count_items_by_key_value(result, 'rel', 'urn:X-bt:rels:hasSensorStream'),
                                1)

    def test_plugin_get_dataset_data(self):
        """
        Test that we can get data from a single dataset within the catalogue.
        """

        connection = self.plugin(self.url,
                                 api_key=self.api_key)
        result = connection[self.dataset].get_data()

        self.assertIsInstance(result, str)
        self.assertGreaterEqual(len(result), 1)
        self.assertIn('c7f361c6-7cb7-4ef5-aed9-397a0c0c4088',
                      result)


class ConnectorHyperCatCiscoTest(TestCase):
    url = 'https://api.cityverve.org.uk/v1/cat'
    subcatalogue = 'https://api.cityverve.org.uk/v1/cat/weather-observations-wind'
    dataset = 'https://api.cityverve.org.uk/v1/entity/weather-observations-wind/132'

    entity_url = 'https://api.cityverve.org.uk/v1/entity'

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

    def test_plugin_get_datasets(self):
        connection = self.plugin(self.url,
                                 api_key=self.api_key)
        datasets = connection.get_datasets()

        self.assertEqual(list,
                         type(datasets))

        self.assertLessEqual(1,
                             len(datasets))

        # Only check a couple of expected results are present - there's too many to list here
        expected = {
            'https://api.cityverve.org.uk/v1/cat/accident',
            'https://api.cityverve.org.uk/v1/cat/advertising-board',
            'https://api.cityverve.org.uk/v1/cat/advertising-post',
            # And because later tests rely on it...
            'https://api.cityverve.org.uk/v1/cat/weather-observations-wind',
        }
        for exp in expected:
            self.assertIn(exp, datasets)

    def test_plugin_get_subcatalogue_metadata(self):
        connection = self.plugin(self.url,
                                 api_key=self.api_key)
        result = connection[self.subcatalogue].get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-hypercat:rels:hasDescription:en',
            'urn:X-hypercat:rels:containsContentType',
            'urn:X-hypercat:rels:hasHomepage',
        ]:
            self.assertIn(property, relations)

        self.assertEqual('CityVerve Public API - weather-observations-wind catalogue',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasDescription:en')['val'])

        self.assertEqual('application/vnd.hypercat.catalogue+json',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:containsContentType')['val'])

        self.assertEqual('https://api.cityverve.org.uk/v1/entity/weather-observations-wind',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasHomepage')['val'])

    def test_plugin_get_subcatalogue_datasets(self):
        connection = self.plugin(self.url,
                                 api_key=self.api_key)
        entity = connection[self.subcatalogue]
        datasets = entity.get_datasets()

        self.assertEqual(list,
                         type(datasets))

        self.assertLessEqual(1,
                             len(datasets))

        # Only check a couple of expected results are present - there's too many to list here
        expected = {
            'https://api.cityverve.org.uk/v1/entity/weather-observations-wind/73',
            'https://api.cityverve.org.uk/v1/entity/weather-observations-wind/79',
            'https://api.cityverve.org.uk/v1/entity/weather-observations-wind/95',
        }
        for exp in expected:
            self.assertIn(exp, datasets)

    def test_plugin_get_subcatalogue_entity_metadata(self):
        connection = self.plugin(self.url,
                                 api_key=self.api_key)
        result = connection[self.subcatalogue][self.dataset].get_metadata()

        for property in [
            'id',
            'uri',
            'type',
            'name',
            'loc',
            'legal',
        ]:
            self.assertIn(property, result)

        self.assertEqual('132',
                         result['id'])

        self.assertEqual('https://api.cityverve.org.uk/v1/entity/weather-observations-wind/132',
                         result['uri'])

        self.assertEqual('weather-observations-wind',
                         result['type'])

        self.assertEqual('Met Office Datapoint Observations - 3031 (Loch Glascarnoch Saws)',
                         result['name'])

        self.assertEqual(dict,
                         type(result['loc']))

        self.assertEqual(list,
                         type(result['legal']))

    def test_plugin_get_subcatalogue_entity_datasets(self):
        connection = self.plugin(self.url,
                                 api_key=self.api_key)
        entity = connection[self.subcatalogue][self.dataset]
        datasets = entity.get_datasets()

        self.assertEqual(list,
                         type(datasets))

        self.assertLessEqual(1,
                             len(datasets))

        expected = [
            'https://api.cityverve.org.uk/v1/entity/weather-observations-wind/132/timeseries/1',
            'https://api.cityverve.org.uk/v1/entity/weather-observations-wind/132/timeseries/2',
            'https://api.cityverve.org.uk/v1/entity/weather-observations-wind/132/timeseries/3',
        ]
        for exp in expected:
            self.assertIn(exp, datasets)
