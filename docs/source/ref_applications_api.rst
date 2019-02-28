.. _ref_applications_api:

Applications API Reference
==========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :doc:`Developer Guide<guide_developer>` first before reading this reference.


Overview
--------

This document provides a schema reference to the PEDASI Applications API which is used by third-party applications to request data, metadata, or provenance records from a PEDASI instance and its data sources.


Using the API
-------------


API Endpoints
^^^^^^^^^^^^^


GET /api/datasources/
^^^^^^^^^^^^^^^^^^^^^

Params:
 TODO
Retrieves the list of all data sources known to PEDASI, that the authenticated user has the ability to see. This will include some sources which they are unable to use, but have not had their details hidden.


GET /api/datasources/<int>/
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retrieves the PEDASI metadata for a given data source, if the authenticated user has the ability to see it.


GET /api/datasources/<int>/metadata/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Params:
Any supported by data source API
Retrieves metadata via an API query to a data source. The authenticated user must have permission to use the given data source.

E.g. A HyperCat catalogue


GET /api/datasources/<int>/metadata/<int>/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
GET /api/datasources/<int>/metadata/<URI>/		(maybe)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retrieves metadata for a single dataset contained within the source via an API query to the data source. The authenticated user must have permission to use the given data source.

E.g. An entry within a HyperCat catalogue


GET /api/datasources/<int>/data/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Params:
Any supported by data source API
In the case where a data source represents a single dataset, retrieve the dataset via an API query to the data source. The authenticated user must have permission to use the given data source.

If the data source does not represent a single dataset, error.


GET /api/datasources/<int>/data/<int>/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
GET /api/datasources/<int>/data/<URI>/			(maybe)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Params:
In the case where a data source represents multiple datasets, retrieve a single dataset via an API query to the data source. The authenticated user must have permission to use the given data source.

If the data source represents a single dataset, error.


GET /api/datasources/<int>/prov/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Params:
TODO
Retrieve all PROV records related to a single data source.


GET /api/datasources/<int>/prov/<int>/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retrieve a single PROV record related to a the data source.


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
