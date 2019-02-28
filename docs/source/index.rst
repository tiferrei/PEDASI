.. _doc-index:

PEDASI v0.9.0
=============

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Overview
--------

Developed as a platform and a service to explore research challenges in data security, privacy, and ethics, PEDASI enables providers of data - particularly `Internet of Things`_ data - to share their data securely within a common catalogue for use by application developers and researchers. Data can either be hosted and made accessible directly within PEDASI as an internal data source, or hosted elsewhere and accessible as an external data source through PEDASI.

An initial deployment of the platform is available at https://dev.iotobservatory.io.

.. _`Internet of Things`: https://en.wikipedia.org/wiki/Internet_of_things


Key Features
------------

PEDASI's key features are:

 - Searchable catalogue of supported data sources registered by data owners
 - Extensible connector interface that currently supports HyperCat and IoTUK Nation Database data sources
 - Dataset discovery and access via a web interface or via an Applications API
 - Queryable and extensible metadata associated with datasets
 - Adoption of W3C PROV-DM specification to track and record dataset creation, update, and access within internal datastore
 - Internally hosted support for read/write NoSQL datastores
 - Functions as a reverse proxy to data sources, returning data from requests exactly as supplied by the data source


Resources
---------

Documentation is available for the following stakeholders:

 - :doc:`Researchers and other end-users<guide_user>`: for users wishing to discover, explore, and make use of datasets using the web interface
 - :doc:`Data or Application Providers<guide_provider>`: for those aiming to provide data or use applications through PEDASI
 - :doc:`System Administrators<guide_administrator>`: for those aiming to deploy and manage PEDASI either for development or production
 - :doc:`Application developers<guide_developer>`: for developers wanting to create applications that access data available through PEDASI

This documentation is also available on `Read the Docs`_.

.. _`Read the Docs`: https://pedasi.readthedocs.io/en/dev


Licence
-------

PEDASI is provided under the MIT licence.


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
