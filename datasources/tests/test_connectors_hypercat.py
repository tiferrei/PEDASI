import itertools
import typing
import unittest

from django.test import TestCase

from decouple import config

from datasources.connectors.base import AuthMethod, BaseDataConnector, HttpHeaderAuth


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


@unittest.skipIf(config('HYPERCAT_CISCO_API_KEY', default=None) is None,
                 'Cisco HyperCat API key not provided')
class ConnectorHyperCatTest(TestCase):
    # TODO find working dataset
    url = 'https://api.cityverve.org.uk/v1/cat'
    subcatalogue = 'https://api.cityverve.org.uk/v1/cat/polling-station'
    dataset = 'https://api.cityverve.org.uk/v1/entity/polling-station/5'

    def _get_connection(self) -> BaseDataConnector:
        return self.plugin(self.url,
                           api_key=self.api_key,
                           auth=HttpHeaderAuth)

    def setUp(self):
        BaseDataConnector.load_plugins('datasources/connectors')
        self.plugin = BaseDataConnector.get_plugin('HyperCat')

        self.api_key = config('HYPERCAT_CISCO_API_KEY')
        self.auth = None

    def test_get_plugin(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_init(self):
        connection = self._get_connection()

        self.assertEqual(connection.location, self.url)

    def test_plugin_type(self):
        connection = self._get_connection()

        self.assertTrue(connection.is_catalogue)

    def test_determine_auth(self):
        connection = self._get_connection()

        auth_method = connection.determine_auth_method(connection.location, connection.api_key)

        self.assertEqual(AuthMethod.HEADER, auth_method)

    def test_plugin_get_catalogue_metadata(self):
        connection = self._get_connection()

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
        connection = self._get_connection()

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
            'https://api.cityverve.org.uk/v1/cat/polling-station',
        }
        for exp in expected:
            self.assertIn(exp, datasets)

    def test_plugin_iter_datasets(self):
        connection = self._get_connection()

        for dataset in connection:
            self.assertEqual(str,
                             type(dataset))

    def test_plugin_len_datasets(self):
        connection = self._get_connection()

        self.assertLessEqual(1,
                             len(connection))

    def test_plugin_iter_items(self):
        """
        Test naive iteration over key-value pairs of datasets within this catalogue.

        This process is SLOW so we only do a couple of iterations.
        """
        connection = self._get_connection()

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
        with self._get_connection() as connection:
            for k, v in itertools.islice(connection.items(), 5):
                self.assertEqual(str,
                                 type(k))

                self.assertIsInstance(v,
                                      BaseDataConnector)

                self.assertEqual(k,
                                 v.location)

    # CityVerve API is discontinued
    @unittest.expectedFailure
    def test_plugin_get_subcatalogue_metadata(self):
        connection = self._get_connection()

        result = connection[self.subcatalogue].get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-hypercat:rels:hasDescription:en',
            'urn:X-hypercat:rels:isContentType',
            'urn:X-hypercat:rels:hasHomepage',
        ]:
            self.assertIn(property, relations)

        self.assertEqual('CityVerve Public API - polling-station catalogue',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasDescription:en')['val'])

        self.assertEqual('application/vnd.hypercat.catalogue+json',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:isContentType')['val'])

        self.assertEqual('https://developer.cityverve.org.uk',
                         _get_item_by_key_value(result, 'rel', 'urn:X-hypercat:rels:hasHomepage')['val'])

    # CityVerve API is discontinued
    @unittest.expectedFailure
    def test_plugin_get_subcatalogue_datasets(self):
        connection = self._get_connection()

        subcatalogue = connection[self.subcatalogue]
        datasets = subcatalogue.get_datasets()

        self.assertEqual(list,
                         type(datasets))

        self.assertLessEqual(1,
                             len(datasets))

        # Only check a couple of expected results are present - there's too many to list here
        expected = {
            'https://api.cityverve.org.uk/v1/entity/polling-station/5',
            'https://api.cityverve.org.uk/v1/entity/polling-station/3',
            'https://api.cityverve.org.uk/v1/entity/polling-station/4',
        }
        for exp in expected:
            self.assertIn(exp, datasets)

    # CityVerve API is discontinued
    @unittest.expectedFailure
    def test_plugin_get_subcatalogue_dataset_metadata(self):
        connection = self._get_connection()

        subcatalogue = connection[self.subcatalogue]
        dataset = subcatalogue[self.dataset]
        result = dataset.get_metadata()

        relations = [relation['rel'] for relation in result]
        for property in [
            'urn:X-cityverve:rels:id',
            'urn:X-cityverve:rels:name',
            'urn:X-cityverve:rels:type',
            'http://www.w3.org/2003/01/geo/wgs84_pos#long',
            'http://www.w3.org/2003/01/geo/wgs84_pos#lat',
            'urn:X-cityverve:rels:entity.district',
            'urn:X-cityverve:rels:entity.ward',
        ]:
            self.assertIn(property, relations)

        self.assertEqual('5',
                         _get_item_by_key_value(result, 'rel', 'urn:X-cityverve:rels:id')['val'])

        self.assertEqual('Cadishead : 5',
                         _get_item_by_key_value(result, 'rel', 'urn:X-cityverve:rels:name')['val'])

        self.assertEqual('polling-station',
                         _get_item_by_key_value(result, 'rel', 'urn:X-cityverve:rels:type')['val'])

    # CityVerve API is discontinued
    @unittest.expectedFailure
    def test_plugin_get_subcatalogue_dataset_data(self):
        connection = self._get_connection()

        subcatalogue = connection[self.subcatalogue]
        dataset = subcatalogue[self.dataset]
        data = dataset.get_data()

        self.assertEqual(list,
                         type(data))

        self.assertEqual(1,
                         len(data))

        data_entry = data[0]

        self.assertEqual(dict,
                         type(data_entry))

        for property in [
            'id',
            'uri',
            'type',
            'name',
            'loc',
            'entity',
            'instance',
            'legal',
        ]:
            self.assertIn(property, data_entry)

        self.assertEqual('5',
                         data_entry['id'])

        self.assertEqual(self.dataset,
                         data_entry['uri'])

        self.assertEqual('polling-station',
                         data_entry['type'])
