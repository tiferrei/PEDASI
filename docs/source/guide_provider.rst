.. _guide_provider:

PEDASI Data And Application Provider Guide
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :doc:`User Guide<guide_user>` first to give you an overview of the PEDASI platform and how to use its features before reading this guide.


Purpose
-------

This guide is for Data or Application Providers wanting to add, update, or remove data sources or applications within a PEDASI instance.


Data Providers: Managing Data Sources
-------------------------------------

In order for users to begin using PEDASI, you should provide access to a range of data sources. The following sections will walk you through adding and managing your first data source. We will use the IoTUK Nation Database API (see https://iotuk.org.uk/iotuk-nation-database-api/) as a basic example.

If you are not a Central Administrator or don't have Data Provider privileges associated with your account, you'll need to obtain these first. Contact the PEDASI Central Administrator to grant these privileges for your account.


Adding a Data Source
^^^^^^^^^^^^^^^^^^^^

Before adding a new data source, first check if the licence type for that data source already exists. Select *Licences* from the navigation bar to display all current licences, and if the licence you need to use isn't already in the list, you'll need to add it as a new licence type. See *Adding a New Data Source Licence* below.

To add a new data source:

 1. Select *Data Sources* from the PEDASI navigation bar to see a list of all data sources to which you have access
 2. Select *New Data Source* from the Data Sources page, and add in details for each of the following fields:

    - *Name*: add in a unique name for this data source, such as 'UKIoT Nations'
    - *Description*: optionally add in some specific details concerning this data source, such as its owner any links or references to any specifications or other documentation regarding the data source and format of the data that is delivered on request, e.g. some of the overview text at https://iotuk.org.uk/projects/iotuk-nation-database%E2%80%8B/ and a link to the page, and perhaps a link to the API details at https://github.com/TheDataCity/IoT-UK-Nation-Database-APIs. If the data source provides partially or fully encrypted data, also specify links to contact information and/or any reference material for obtaining a means to encrypt the data (not required for IoTUK Nations)
    - *Url*: specify the base API URL for this data source, e.g. https://api.iotuk.org.uk/iotOrganisation.
    - *Api key*: optionally specify an API key if one is required for PEDASI to access this resource
    - *Plugin name*: select an appropriate data connector to interface with this API, e.g. DataSetConnector
    - *Licence*: select an appropriate licence from those available in the dropdown list, e.g. Open Database Licence.
    - *Is encrypted*: select this if the data supplied from the data source is partially or fully encrypted, e.g. leave unselected
    - *Public permission level*: see the *Requesting Access to a Data Source* section in the :doc:`User Guide<guide_user>` for a breakdown of the different levels of access you can specify for a data source. e.g. DATA (which is the default)
    - *Prov exempt*: select this if user activity tracking should be enabled for this data source, e.g. leave unselected

 3. Then select 'Create' to create this data source, and you'll be presented with an overview page for that data source.

The next stage is to add in metadata for each of the parameters that can be used within the API. This step isn't mandatory, since arbitrary parameters can be specified via the Applications API or from within the Data Explorer, but is recommended. From the data source overview page, for each API query parameter (e.g. town, year, postcode for the IoTUK Nation Database data source):

 1. In the *Metadata* section, select *data_query_param* from the first dropdown
 2. Add the name of the API query field to the *Value* textbox, e.g. 'town'
 3. Select *Add* to add this query parameter

Once complete, your data source is ready to use.


Updating a Data Source
^^^^^^^^^^^^^^^^^^^^^^

To edit details for an existing data source:

 1. Select *Data Sources* from the navigation bar to see a list of all data sources to which you have access
 2. Select *Detail* for the data source you wish to edit
 3. Select *Edit* to edit the data source's details
 4. Edit the fields as instructed in the *Adding a Data Source* section
 5. Select *Update* to update the data source's details


Removing a Data Source
^^^^^^^^^^^^^^^^^^^^^^

To remove an existing data source:

 1. Select *Data Sources* from the navigation bar to see a list of all data sources to which you have access
 2. Select *Detail* for the data source you wish to remove
 3. Select *Delete* to indicate you wish to remove the data source
 4. Select *Delete* to confirm you wish to remove this data source


Adding a New Data Source Licence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need to add a new type of licence for a data source:

 1. Select *Licences* from the navigation bar to display all current licences
 2. Select *New License* to create a new licence
 3. Add detail for the following fields:

    - *Name*: add a full name for a new licence, e.g. Open Database Licence
    - *Short name*: add a short name for the licence, typically an acronym, e.g. ODbL
    - *Version*: add the version number for the licence to use
    - *URL*: add a link to an online resource describing the full terms of the licence

 4. Select 'Create' to create the licence, and you'll be presented with an overview page for that licence.


Approving Data Access Requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To approve user or application requests for amended access rights to data sources:

 1. Select *Data Sources* from the navigation bar to see a list of all data sources to which you have access
 2. Select *Detail* for the data source you wish to manage access on
 3. Select *Manage Access* to list access requests and manage those requests. You'll see the level of access requested for each user, their current access level, and the reason for the request
 4. Select either:

    - *Approve*: to approve the request
    - *Edit*: to amend the request's access privileges and data push rights (if data push is supported for this data source)
    - *Reject*: to reject the request


Application Providers: Managing Applications
--------------------------------------------

In order for a developer to access PEDASI's capabilities within their application, their application needs to be first registered within PEDASI in order to obtain an API key they can use to authenticate with PEDASI. The following sections will walk you through adding and managing your first application. We will use the IoTUK Nation Map Demo application (see https://github.com/Southampton-RSG/app-iotorgs-map) as a basic example.

If you are not a Central Administrator or don't have Application Provider privileges associated with your account, you'll need to obtain these first. Contact the Central Administrator to request these privileges for your account.


Adding an Application
^^^^^^^^^^^^^^^^^^^^^

To add a new application:

 1. Select *Applications* from the PEDASI navigation bar to see a list of all applications to which you have access
 2. Select *New Application* from the Applications page, and add in details for each of the following fields:

    - *Name*: add a full name for the application, e.g. IoTUK Nation Map Demo
    - *Description*: add a brief description of the application, including what it aims to achieve using PEDASI
    - *Url*: specify a public URL for the deployed application itself if it's web-based, or alternatively a source code repository URL if one exists, e.g. https://github.com/Southampton-RSG/app-iotorgs-map
    - *Access control*: specify whether the application details are publicly viewable, e.g. leave unselected

 3. Select *Create* to register the new application within PEDASI, and you'll be presented with an overview page for that application, with a new API key

The API key is what will be used by the developer to authenticate with PEDASI from their application, with the application acting as a user within the system.


Updating an Application
^^^^^^^^^^^^^^^^^^^^^^^

 1. Select *Applications* from the PEDASI navigation bar to see a list of all applications to which you have access
 2. Select *Detail* for the application you wish to edit. From here, you can also:

    - Select *Revoke API Token*: to revoke the current API token which will prohibit its further use within PEDASI
    - *If an API token has been revoked*, select *Generate API Token* to generate a new API token for this application

 3. Select *Edit* to edit the application's details
 4. Edit the fields as instructed in the *Adding an Application* section
 5. Select *Update* to update the data source's details


Obtaining Access to Data Sources for Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As with users, applications also require access rights to data sources that are not public. By default, data sources are created with DATA access permissions and are considered public (awarding access to both data source metadata and data for all users, but not provenance records).

If a data source has a lower level of access than required by the application, a request should be made from the Application Provider on behalf of their application for an appropriate level of access (typically DATA, the default). See *Requesting Access to a Data Source* in the :doc:`User Guide<guide_user>`.


Removing an Application
^^^^^^^^^^^^^^^^^^^^^^^

To remove an application:

 1. Select *Applications* from the PEDASI navigation bar to see a list of all applications to which you have access
 2. Select *Detail* for the application you wish to remove
 3. Select *Delete* to indicate you wish to remove this application
 4. Select *Delete* to confirm you wish to remove this application


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
