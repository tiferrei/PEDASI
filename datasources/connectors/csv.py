import csv
import json
import typing

from django.http import JsonResponse

import mongoengine
from mongoengine import context_managers

from .base import DataSetConnector


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
    """
    pass


def _type_convert(val):
    """
    Attempt to convert a value into a numeric type.

    :param val: Value to attempt to convert
    :return: Converted value or unmodified value if conversion was not possible
    """
    for t in (int, float):
        try:
            return t(val)

        except ValueError:
            pass

    return val


class CsvToMongoConnector(DataSetConnector):
    def clear(self):
        with context_managers.switch_collection(CsvRow, self.location) as CsvRowCollection:
            CsvRowCollection.objects.delete()

    def post_data(self, data: typing.Union[typing.MutableMapping[str, str],
                                           typing.List[typing.MutableMapping[str, str]]]):
        def create_document(row: typing.MutableMapping[str, str]):
            kwargs = {key: _type_convert(val) for key, val in row.items()}

            # TODO make id column more general
            if 'id' in kwargs:
                kwargs['x_id'] = kwargs.pop('id')

            return kwargs

        # Put data in collection belonging to this data source
        with context_managers.switch_collection(CsvRow, self.location) as CsvRowCollection:
            collection = CsvRowCollection._get_collection()

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
        params = {key: _type_convert(val) for key, val in params.items()}

        with context_managers.switch_collection(CsvRow, self.location) as CsvRowCollection:
            records = CsvRowCollection.objects.filter(**params)

            data = json.loads(records.exclude('_id').to_json())
            # TODO make id column more general
            for item in data:
                if 'x_id' in item:
                    item['id'] = item.pop('x_id')

            return JsonResponse({
                'status': 'success',
                'data': data,
            })
