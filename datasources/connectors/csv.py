import pathlib
import typing

from django.conf import settings

from .base import DataSetConnector, DummyRequestsResponse


# TODO this still allows users to access the data of other users
def in_permitted_directory(path: typing.Union[pathlib.Path, str]) -> bool:
    """
    Is the file being accessed in a permitted directory?

    Permitted directories are:
    - MEDIA_ROOT
    - BASE_DIR/data - if in debug mode

    :param path: File path to check
    :return: Is file in a permitted directory?
    """
    path = pathlib.Path(path)
    root_path = pathlib.Path(settings.MEDIA_ROOT)
    test_files_path = pathlib.Path(settings.BASE_DIR).joinpath('data')

    if root_path in path.parents:
        return True

    elif settings.DEBUG and test_files_path in path.parents:
        return True

    return False


class CsvConnector(DataSetConnector):
    """
    Data connector for retrieving data from CSV files.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 **kwargs):
        if not in_permitted_directory(location):
            raise PermissionError('File being accessed is not within the permitted directory')

        super().__init__(location, api_key, auth, **kwargs)

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Return a dummy response from a CSV file.

        :param params: Optional query parameter filters - ignored
        :return: Requested data
        """
        with open(self.location, 'r') as f:
            return DummyRequestsResponse(f.read(), 200, 'text/plain')
