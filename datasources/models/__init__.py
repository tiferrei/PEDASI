"""
This package contains the :class:`DataSource` model representing an internal or
external data source and the models necessary to support it.
"""

from .datasource import (
    Licence,
    UserPermissionLevels,
    UserPermissionLink,
    DataSource
)

from .metadata import (
    MetadataField,
    MetadataItem
)


from .quality import (
    QualityRuleset,
    QualityLevel,
    QualityCriterion
)
