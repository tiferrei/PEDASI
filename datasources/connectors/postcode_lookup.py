"""
Postcode connector.

Run as module with --import <csv file> to import a postcode database CSV.
"""

import csv
import sys
import typing

from django.http import JsonResponse

from decouple import config
import sqlalchemy
from sqlalchemy.exc import NoSuchTableError
import sqlalchemy.orm

from .base import DataSetConnector


class OnsPostcodeDirectoryConnector(DataSetConnector):
    _table_name = 'connector_postcode'

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None):
        super().__init__(location, api_key=api_key, auth=auth)

        self._engine = sqlalchemy.create_engine(config('DATABASE_URL'))
        self._session_maker = sqlalchemy.orm.sessionmaker(bind=self._engine)

        try:
            self._table_meta = sqlalchemy.MetaData(self._engine)
            self._table = sqlalchemy.Table(self._table_name, self._table_meta, autoload=True)

        except NoSuchTableError as e:
            raise FileNotFoundError('Postcode table is not present') from e

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        if params is None or 'postcode' not in params:
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'postcode': 'postcode is a required field',
                },
            }, status=400)

        query = sqlalchemy.select(
            [self._table]
        ).where(self._table.c.postcode == params['postcode'].replace(' ', '').upper())

        result = self._session_maker().execute(query).fetchone()

        try:
            return JsonResponse(dict(result), json_dumps_params={'default': str})

        except TypeError:
            # Did not return a valid result
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'postcode': 'no record matching postcode \'{0}\' found'.format(params['postcode']),
                },
            }, status=400)

    @classmethod
    def setup(cls, filename):
        engine = sqlalchemy.create_engine(config('DATABASE_URL'))

        metadata = sqlalchemy.MetaData(engine)
        postcodes = sqlalchemy.Table(
            cls._table_name, metadata,
            sqlalchemy.Column('postcode', sqlalchemy.String(length=10), index=True, nullable=False, primary_key=True),
            sqlalchemy.Column('lat', sqlalchemy.Float, nullable=False),
            sqlalchemy.Column('long', sqlalchemy.Float, nullable=False)
        )

        try:
            postcodes.create()

        except sqlalchemy.exc.OperationalError:
            pass

        conn = engine.connect()

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            # TODO this fails if any row already exists - but checking each row in turn is slow - find solution
            conn.execute(postcodes.insert(), [
                {'postcode': row['pcds'].replace(' ', '').upper(), 'lat': row['lat'], 'long': row['long']} for row in reader
            ])


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--import':
        OnsPostcodeDirectoryConnector.setup(sys.argv[2])

    else:
        print(__doc__)
