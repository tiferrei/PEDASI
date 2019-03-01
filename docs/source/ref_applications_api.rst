.. _ref_applications_api:

Applications API Reference
==========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :doc:`Developer Guide<guide_developer>` first before reading this reference; it contains examples on how to use the API.


Overview
--------

This document provides a schema reference to the PEDASI Applications API which is used by third-party applications to request data, metadata, or provenance records from a PEDASI instance and its data sources.


API Endpoints
-------------

--------

GET /api/datasources/
^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieves the list of all data sources known to PEDASI, that the authenticated user has the ability to see. This will include some sources which they are unable to use, but have not had their details hidden.

Parameters:
  None

Response class (Status 200): application/json
  .. code-block:: json

     [
       {
         "id": 0,
         "name": "string",
         "description": "string",
         "url": "string",
         "plugin_name": "string",
         "licence": {
           "name": "string",
           "short_name": "string",
           "version": "string",
           "url": "string"
         },
         "is_encrypted": true,
         "encrypted_docs_url": "string",
         "metadata_items": [
           {
             "field": {
               "name": "string",
               "short_name": "string"
             },
             "value": "string"
           }
         ]
       }
     ]

Responses messages:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - HTTP Status Code
       - Reason
       - Response

     * - 
       - 
       - 

--------

GET /api/datasources/{datasource_id}/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieves the PEDASI metadata for a given data source, if the authenticated user has the ability to see it.

Parameters:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - Parameter
       - Description
       - Type

     * - datasource_id
       - The numeric id of the data source
       - integer

Response class (Status 200): application/json
  .. code-block:: json

     {
       "id": 0,
       "name": "string",
       "description": "string",
       "url": "string",
       "plugin_name": "string",
       "licence": {
         "name": "string",
         "short_name": "string",
         "version": "string",
         "url": "string"
       },
       "is_encrypted": true,
       "encrypted_docs_url": "string",
       "metadata_items": [
         {
           "field": {
             "name": "string",
             "short_name": "string"
           },
           "value": "string"
         }
       ]
     }
     
--------

GET /api/datasources/{datasource_id}/metadata/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieves metadata for a given data source via an API query to the data source, if supported by the data source. The authenticated user must have META permissions or above to access the data source. E.g. A HyperCat catalogue

Parameters:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - Parameter
       - Description
       - Type

     * - datasource_id
       - The numeric id of the data source
       - integer

--------

GET /api/datasources/{datasource_id}/metadata/{dataset_id}/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
GET /api/datasources/{datasource_id}/metadata/{dataset_uri}/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieves metadata for a single dataset contained within the given data source via an API query to the data source. The authenticated user must have permission to use the given data source. E.g. An entry within a HyperCat catalogue

Parameters:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - Parameter
       - Description
       - Type

     * - datasource_id
       - The numeric id of the data source
       - integer

     * - dataset_id
       - The numeric id of the data set within the specific data source
       - integer

     * - dataset_uri
       - The uri of the data set within the specific data source
       - integer

--------

GET /api/datasources/{datasource_id}/data/?{query_string}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  In the case where a data source represents a single dataset, retrieve the dataset via an API query to the data source using the given query string. The authenticated user must have permission to use the given data source.
  If the data source does not represent a single dataset, error.

Parameters:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - Parameter
       - Description
       - Type

     * - datasource_id
       - The numeric id of the data source
       - integer

     * - query_string
       - An ampersand-separated set of key=value pairs
       - string

Response class (Status 200): application/json
  Dependent on data source

--------

GET /api/datasources/{datasource_id}/data/{dataset_id}/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
GET /api/datasources/{datasource_id}/data/{dataset_uri}/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  In the case where a data source represents multiple datasets, retrieve a single dataset via an API query to the data source. The authenticated user must have permission to use the given data source.
  If the data source represents a single dataset, error.

Parameters:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - Parameter
       - Description
       - Type

     * - datasource_id
       - The numeric id of the data source
       - integer

     * - dataset_id
       - The numeric id of the data set within the specific data source
       - integer

     * - dataset_uri
       - The uri of the data set within the specific data source
       - integer

Response class (Status 200): application/json
  Dependent on data source

--------

GET /api/datasources/{datasource_id}/prov/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieve all PROV records related to a single data source.

Parameters:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - Parameter
       - Description
       - Type

     * - datasource_id
       - The numeric id of the data source
       - integer

Response class (Status 200): application/json
  .. code-block:: json

     {
       "prov": [
         {
           "_id": {
             "$oid": "string"
           },
           "prefix": {
             "piot": "string",
             "foaf": "string"
           },
           "entity": {
             "string": {
               "prov:type": "string",
               "xsd:anyURI": "string"
             }
           },
           "activity": {
             "string": {
               "prov:startTime": "string",
               "prov:type": "string"
             }
           },
           "agent": {
             "string": {
               "prov:type": "string"
             },
             "piot:app-pedasi": {
               "prov:type": "string",
               "xsd:anyURI": "string"
             }
           },
           "actedOnBehalfOf": {
             "_:id1": {
               "prov:delegate": "string",
               "prov:responsible": "string",
               "prov:activity": "string",
               "prov:type": "string"
             }
           }
         }
       ]
     }

--------

GET /api/datasources/{datasource_id}/prov/{dataset_id}/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieve a single PROV record related to a data source.

Parameters:
  .. list-table::
     :widths: 16 80 16
     :header-rows: 1

     * - Parameter
       - Description
       - Type

     * - datasource_id
       - The numeric id of the data source
       - integer

     * - dataset_id
       - The numeric id of the data set within the specific data source
       - integer

     * - dataset_uri
       - The uri of the data set within the specific data source
       - integer

--------

References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
