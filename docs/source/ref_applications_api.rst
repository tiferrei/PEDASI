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


API Endpoints - General
-----------------------

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
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - List of data sources
       - Successful
       - application/json

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

Responses messages:
  .. list-table::
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - Single data source
       - Successful
       - application/json

     * - 404
       - .. code-block:: json

            {
                "detail": "Not found."
            }

       - Parameter datasource_id was not valid
       - application/json

--------

GET /api/datasources/{datasource_id}/metadata/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieves metadata for a given data source which may include an API query to the data source, if supported by the data source. The authenticated user must have META permissions or above to access the data source. In the general case, this is implementation-specific for the data connector, in the case of a HyperCat catalogue, it presents the catalogue record for that dataset.

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
  Dependent on data source

Responses messages:
  .. list-table::
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - Data source metadata
       - Successful
       - application/json

     * - 400
       - .. code-block:: json

            {
                "status": "error",
                "message": "Data source does not provide metadata"
            }

       - Data source/connector does not support metadata queries
       - application/json

     * - 404
       - .. code-block:: json

            {
                "detail": "Not found."
            }

       - Parameter datasource_id was not valid
       - application/json

     * - any other
       - Error response from external data source
       - An error occured within the external data source
       - determined by data source

--------

GET /api/datasources/{datasource_id}/data/?{query_string}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  In the case where a data source represents a single dataset, retrieve the dataset via an API query to the data source using the given query string. The authenticated user must have permission to use the given data source.

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

Response class (Status 200): type-specific to datasource
  Dependent on data source

Responses messages:
  .. list-table::
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - Data source data
       - Successful
       - determined by data source

     * - 400
       - .. code-block:: json

            {
                "status": "error",
                "message": "Data source does not provide data"
            }

       - Data source/connector does not support data queries
       - application/json

     * - 404
       - .. code-block:: json

            {
                "detail": "Not found."
            }

       - Parameter datasource_id was not valid
       - application/json

     * - any other
       - Error response from external data source
       - An error occured within the external data source
       - determined by data source

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

Responses messages:
  .. list-table::
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - Data source PROV records
       - Successful
       - application/json

     * - 404
       - .. code-block:: json

            {
                "detail": "Not found."
            }

       - Parameter datasource_id was not valid
       - application/json

--------

API Endpoints - Catalogues
--------------------------

Data catalogues are a subset of data sources which contain a number of distinct data sets.

--------

GET /api/datasources/{datasource_id}/datasets/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Retrieves the list of dataset IDs within a catalogue, which may be via an API query to the data source, if supported by the data source. The authenticated user must have META permissions or above to access the data source. In the general case, this is implementation-specific for the data connector.

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
         "status": "success",
         "data": [
             "string"
         ]

Responses messages:
  .. list-table::
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - Data source list of datasets
       - Successful
       - application/json

     * - 400
       - .. code-block:: json

            {
                "status": "error",
                "message": "Data source does not contain datasets"
            }

       - Data source/connector is not a catalogue
       - application/json

     * - 404
       - .. code-block:: json

            {
                "detail": "Not found."
            }

       - Parameter datasource_id was not valid
       - application/json

     * - any other
       - Error response from external data source
       - An error occured within the external data source
       - determined by data source

--------

GET /api/datasources/{datasource_id}/datasets/{dataset_id}/metadata/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  Specific to data sources which purport to act as catalogues of data, it retrieves metadata for a single dataset contained within the given data source in most cases via an API query to the data source (e.g. HyperCat), although is dependent on data connector implementation. The authenticated user must have permission to use the given data source.

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
       - The id of the data set within the specific data source, which may be a URI
       - string

Response class (Status 200): application/json
  Dependent on data source

Responses messages:
  .. list-table::
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - Data set metadata
       - Successful
       - application/json

     * - 400
       - .. code-block:: json

            {
                "status": "error",
                "message": "Data source does not provide metadata"
            }

       - Data source/connector does not support metadata queries
       - application/json

     * - 404
       - .. code-block:: json

            {
                "detail": "Not found."
            }

       - Parameter datasource_id was not valid
       - application/json

     * - 404
       - .. code-block:: json

            {
                "status": "error",
                "message": "Data set does not exist within this data source"
            }

       - Parameter dataset_id did not refer to a valid dataset within this data source
       - application/json

     * - any other
       - Error response from external data source
       - An error occured within the external data source
       - determined by data source

--------


GET /api/datasources/{datasource_id}/datasets/{dataset_id}/data/?{query_string}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementation notes:
  In the case where a data source represents a catalogue of datasets, retrieve a single dataset via an API query to the data source. The authenticated user must have permission to use the given data source.

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
       - The id of the data set within the specific data source, which may be a URI
       - string

     * - query_string
       - An ampersand-separated set of key=value pairs
       - string

Response class (Status 200): type-specific to datasource
  Dependent on data source

Responses messages:
  .. list-table::
     :widths: 16 80 16 16
     :header-rows: 1

     * - HTTP Status Code
       - Response
       - Reason
       - Response Type

     * - 200
       - Data set data
       - Successful
       - application/json

     * - 400
       - .. code-block:: json

            {
                "status": "error",
                "message": "Data source does not provide data"
            }

       - Data source/connector does not support data queries
       - application/json

     * - 404
       - .. code-block:: json

            {
                "detail": "Not found."
            }

       - Parameter datasource_id was not valid
       - application/json

     * - 404
       - .. code-block:: json

            {
                "status": "error",
                "message": "Data set does not exist within this data source"
            }

       - Parameter dataset_id did not refer to a valid dataset within this data source
       - application/json

     * - any other
       - Error response from external data source
       - An error occured within the external data source
       - determined by data source

--------


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
