"""
This module contains the search index definitions for the datasource app using Haystack.

See https://django-haystack.readthedocs.io/en/master/ for documentation.
"""

from haystack import indexes


from . import models


class DataSourceIndex(indexes.SearchIndex, indexes.Indexable):
    """
    The search index definition for a DataSource.

    Uses templates/search/indexes/datasources/datasource_text.txt and
    :meth:`datasources.models.DataSource.search_representation`.
    """
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return models.DataSource
