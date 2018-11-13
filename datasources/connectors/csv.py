import typing

from .base import DataSetConnector, DummyRequestsResponse


class CsvConnector(DataSetConnector):
    """
    Data connector for retrieving data from CSV files.
    """
    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Return a dummy response from a CSV file.

        :param params: Optional query parameter filters - ignored
        :return: Requested data
        """
        with open(self.location, 'r') as f:
            return DummyRequestsResponse(f.read(), 200, 'text/plain')
