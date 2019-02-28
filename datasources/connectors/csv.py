"""
Connectors for handling CSV data.
"""

import csv
import typing

from django.http import JsonResponse

import mongoengine
from mongoengine import context_managers

from .base import DataSetConnector, InternalDataConnector


class CsvConnector(DataSetConnector):
    """
    Data connector for retrieving data from CSV files.
    """
    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Return a JSON response from a CSV file.

        :param params: Query params - ignored
        :return: Metadata
        """
        with open(self.location, 'r') as csvfile:
            # Requires a header row
            reader = csv.DictReader(csvfile)
            return reader.fieldnames

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Return a JSON response from a CSV file.

        CSV file must have a header row with column titles.

        :param params: Optional query parameter filters
        :return: Requested data
        """
        try:
            with open(self.location, 'r') as csvfile:
                # Requires a header row
                reader = csv.DictReader(csvfile)

                if params is None:
                    params = {}

                rows = []
                for row in reader:
                    for key, value in params.items():
                        try:
                            if row[key].strip() != value.strip():
                                break

                        except KeyError:
                            # The filter field isn't in the data so no row can satisfy it
                            break

                    else:
                        # All filters match
                        rows.append(dict(row))

            return JsonResponse({
                'status': 'success',
                'data': rows,
            })

        except UnicodeDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid CSV file',
            }, status=500)


class CsvRow(mongoengine.DynamicDocument):
    """
    MongoDB dynamic document to store CSV data.

    Store in own database - distinct from PROV data.
    Collection must be changed manually when managing CsvRows since all connectors use the same backing model.
    """
    meta = {
        'db_alias': 'internal_data',
    }


def _type_convert(val):
    """
    Attempt to convert a value into a numeric type.

    :param val: Value to attempt to convert
    :return: Converted value or unmodified value if conversion was not possible
    """
    for conv in (int, float):
        try:
            return conv(val)

        except ValueError:
            pass

    return val


class CsvToMongoConnector(InternalDataConnector, DataSetConnector):
    """
    Data connector representing an internally hosted data source, backed by MongoDB.

    This connector allows data to be pushed as well as retrieved.
    """
    id_field_alias = '__id'

    def clean_data(self, **kwargs):
        index_fields = kwargs.get('index_fields', None)

        if index_fields is None:
            return

        if isinstance(index_fields, str):
            index_fields = [index_fields]

        with context_managers.switch_collection(CsvRow, self.location) as collection:
            for index_field in index_fields:
                collection.create_index(index_field, background=True)

    def clear_data(self):
        with context_managers.switch_collection(CsvRow, self.location) as collection:
            collection.objects.delete()

    def post_data(self, data: typing.Union[typing.MutableMapping[str, str],
                                           typing.List[typing.MutableMapping[str, str]]]):
        def create_document(row: typing.MutableMapping[str, str]):
            kwargs = {key: _type_convert(val) for key, val in row.items()}

            # Can't store field 'id' in document - rename it
            if 'id' in kwargs:
                kwargs[self.id_field_alias] = kwargs.pop('id')

            return kwargs

        # Put data in collection belonging to this data source
        with context_managers.switch_collection(CsvRow, self.location) as collection:
            collection = collection._get_collection()

            try:
                # Data is a dictionary - a single row
                collection.insert_one(create_document(data))

            except AttributeError:
                # Data is a list of dictionaries - multiple rows
                documents = (create_document(row) for row in data)
                collection.insert_many(documents)

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        # TODO accept parameters provided twice as an inclusive OR
        if params is None:
            params = {}
        params = {key: _type_convert(val) for key, val in params.items()}

        with context_managers.switch_collection(CsvRow, self.location) as collection:
            records = collection.objects.filter(**params).exclude('_id')

            data = list(records.as_pymongo())

            # Couldn't store field 'id' in document - recover it
            for item in data:
                try:
                    item['id'] = item.pop(self.id_field_alias)

                except KeyError:
                    pass

            return JsonResponse({
                'status': 'success',
                'data': data,
            })
