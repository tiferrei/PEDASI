import typing

from .base import DataSetConnector


class DummyResponse:
    def __init__(self,
                 text: str,
                 status_code: int,
                 content_type: str):
        self.text = text
        self.status_code = status_code
        self.headers = {
            'content-type': content_type,
        }


class CsvConnector(DataSetConnector):
    """
    Data connector for retrieving data from CSV files.
    """
    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        raise NotImplementedError('CSV does not provide metadata')

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        raise NotImplementedError('CSV does not provide metadata')

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Return a dummy response from a CSV file.

        :param params: Optional query parameter filters - ignored
        :return: Requested data
        """
        with open(self.location, 'r') as f:
            return DummyResponse(f.read(), 200, 'text/plain')
