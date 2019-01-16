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


class CsvToMongoConnector(DataSetConnector):
    @staticmethod
    def _flatten_params(params: typing.Optional[typing.Mapping[str, typing.List[str]]]):
        result = {}

        if params is None:
            return result

        for key, val_list in params.items():
            if len(val_list) != 1:
                raise ValueError('A query parameter was provided twice')

            val = val_list[0]
            try:
                result[key] = int(val)

            except ValueError:
                try:
                    result[key] = float(val)

                except ValueError:
                    result[key] = val

        return result

    def post_data(self, data: typing.Union[typing.Mapping, typing.List[typing.Mapping]]):
        # Put data in collection belonging to this data source
        with context_managers.switch_collection(CsvRow, self.location) as CsvRowCollection:
            try:
                CsvRowCollection(**data).save()

            except TypeError:
                for row in data:
                    CsvRowCollection(**row).save()

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        with context_managers.switch_collection(CsvRow, self.location) as CsvRowCollection:
            data = CsvRowCollection.objects

            # TODO accept parameters provided twice as an inclusive OR
            params = self._flatten_params(params)
            data = data(**params)

            return JsonResponse({
                'status': 'success',
                'data': json.loads(data.exclude('_id').to_json()),
            })
