.. _guide_developer:

PEDASI Developer Guide
======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :doc:`User Guide<guide_user>` first to give you an overview of the PEDASI platform before reading this guide.


Purpose
-------

This guide is for application developers wanting to understand how to set up a development environment for PEDASI and develop PEDASI applications.


Developing an Application
-------------------------

The following sections will walk you through using the PEDASI Applications API in your own applications. We will use the JavaScript IoTUK Nation Map Demo application (see https://github.com/Southampton-RSG/app-iotorgs-map) as a basic example. These instructions assume you are aiming to develop against a production deployment of PEDASI managed buy a Central Administrator, but you can also use a local development deployment if you wish. This section assumes you already have a registered PEDASI account,


Adding Required Data Sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Firstly, you'll need to ensure that the data sources your application aims to use are added to PEDASI, which require Data Provider account privileges. If you do not already have these privileges on your PEDASI account, either:

 - Contact your local PEDASI Data Provider to register the data sources
 - Contact the PEDASI Central Administrator to register the data sources
 - Contact the PEDASI Central Administrator to request Data Provider privileges for your account

For simplicity, this guide assumes that the data source is being added with a public level of access (i.e. at the DATA level), so that the application will not need to have its access level approved via a request.

If you now have these privileges and wish to add the data sources yourself, follow the *Adding a Data Source* section in the :doc:`Data and Application Provider Guide<guide_provider>` (which also contains details for adding the IoTUK Nation Data as a data source).

Once these data source(s) have been registered, note the API query URL for each of them that you intend to use in your application. For each data source, this can be obtained by visiting the *Detail* page for a data source from the data sources list, which you can find via the *Data Sources* link in the PEDASI top navigation bar.


Obtaining an Application API Key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will first need to register some basic application details to obtain an API key for your application to authenticate with PEDASI, which requires Application Provider account privileges. If you do not have these privileges on your PEDASI account, either:

 - Contact your local PEDASI Application Provider to register the application and obtain an API key
 - Contact the PEDASI Central Administrator to register the new application and obtain an API key
 - Contact the PEDASI Central Administrator to request Application Provider privileges for your account

If you now have these privileges and wish to add the application yourself, follow the *Adding an Application* section in the :doc:`Data and Application Provider Guide<guide_provider>` (which also contains details for adding the IoTUK Nation Map Demo application).


Code Examples
^^^^^^^^^^^^^

Once you have the required data sources and application set up in PEDASI, you can begin using the API. For example, with the IoTUK Nations Database, assuming the API query URL for it is https://dev.iotobservatory.io/api/datasources/2/data.


Using cURL
~~~~~~~~~~

An easy way to first test and see the output is using the command line tool *cURL* available under Linux (and installable on Mac OS X), which allows you to make requests from a RESTful API and see the results. Strictly speaking, since we're assuming it is using a publicly accessible data source, we do not need to supply any application API key. However, for completeness and for best practice, we can include it in the request:

.. code-block:: console

   $ curl -H "Authorization: Token <api_key>" "https://dev.iotobservatory.io/api/datasources/2/data/?town=Southampton"

Then we should see something like the following (although without the formatting):

.. code-block:: none

   {
     "results": 9,
     "data": {
         "1": {
             "organisation_id": "2018_590",
             "organisation_name": "2IC LIMITED",
             "organisation_type": "ltd",
   ...


Using Python
~~~~~~~~~~~~

We can duplicate the cURL request above in Python 3. Creating a new Python file (e.g. *api-test.py*) with the following contents:

.. code-block:: python

   import sys
   import requests

   url = "https://dev.iotobservatory.io/api/datasources/2/data/?town=Southampton"
   headers = {
       'Authorization': 'Token <api_key>'
   }
   response = requests.get(url, headers=headers)
   print(response)

We can run this example using:

.. code-block:: console

   $ python api-test.py

Which should display the same output as we saw with cURL.


Using JavaScript - a Basic Example Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An `example`_ hosted on GitHub is a lightweight JavaScript PEDASI web application that uses the PEDASI Applications API - see the GitHub repository and its README for more details on how to deploy and use it.

.. _`example`: https://github.com/PEDASI/app-iotorgs-map


Application API Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :doc:`Applications API Reference<ref_applications_api>` documentation covers the API and its endpoints, and how to use it.


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
