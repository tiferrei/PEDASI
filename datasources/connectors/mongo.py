import json
import typing

import pymongo

from .base import DataSetConnector, DummyRequestsResponse


class UnmanagedMongoConnector(DataSetConnector):
    """
    This connector handles requests for data from a MongoDB collection managed outside of PEDASI.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 **kwargs):
        super().__init__(location, api_key, auth, **kwargs)

        # TODO validate db url
        host, database, collection = location.rsplit('/', 2)
        self._client = pymongo.MongoClient(host)
        self._database = self._client[database]
        self._collection = self._database[collection]

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Select and return all contents of table.
        """
        result = self._collection.find(filter=params)

        return DummyRequestsResponse(
            json.dumps([dict(row) for row in result], default=str),
            200, content_type='application/json'
        )
