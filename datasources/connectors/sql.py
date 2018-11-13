"""
This module contains data connectors for SQL tables.

These tables may be external or automatically manage by PEDASI.
"""

import typing

import sqlalchemy
import sqlalchemy.orm

from .base import DataSetConnector


class UnmanagedSqlConnector(DataSetConnector):
    """
    This connector handles requests for data from an SQL table outside of PEDASI.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 **kwargs):
        super().__init__(location, api_key, auth, **kwargs)

        # TODO validate db url
        db_url, table = location.rsplit('/', 1)

        self._engine = sqlalchemy.create_engine(db_url, echo=True)
        self._session_maker = sqlalchemy.orm.sessionmaker(bind=self._engine)

        self._table_meta = sqlalchemy.MetaData(self._engine)
        self._table = sqlalchemy.Table(table, self._table_meta, autoload=True)

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        # TODO select where params
        """
        Select and return all contents of table.
        """
        session = self._session_maker()

        query = sqlalchemy.select([self._table])
        result = session.execute(query)

        return list(result)

    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get metadata for an SQL table outside of PEDASI.
        """
        columns = [col.name for col in self._table.columns]

        return {
            'columns': columns
        }
