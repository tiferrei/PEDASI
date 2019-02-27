.. _guide_administrator:

PEDASI Administration Guide
===========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :ref:`User Guide<guide_user>` first to give you an overview of the PEDASI platform and how to use its features before reading this guide.


Purpose
-------

This guide is for System Administrators aiming to deploy a PEDASI instance, and Data or Application Providers wanting to add, update, or remove data sources or applications within a PEDASI instance.


System Administrators: Deploying PEDASI in Production
-----------------------------------------------------

Overview
^^^^^^^^

A deployment of PEDASI is done automatically to a remote Ubuntu server via a preconfigured Ansible script, which performs the following tasks:

 1. Install system and webserver prerequisites
 2. Configure databases
 3. Deploy PEDASI
 4. Configure and start webserver


Prerequisites
^^^^^^^^^^^^^

Ensure you have the following prerequisites before you begin:

 - Ubuntu 18.04 LTS server with:

   - The latest security updates
   - A static IP address
   - A user account with external SSH access enabled and with sudo access privileges (e.g. 'ubuntu' - ubuntu will be used throughout this documentation) 

 - A Linux or Mac OS X local machine with the following installed:

   - Ansible v2.7.1 or above
   - Git command line client v2 or above


Cloning the PEDASI Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On your local machine, first clone the PEDASI repository:

.. code-block:: console

   $ git clone https://github.com/PEDASI/PEDASI.git


Configuration
^^^^^^^^^^^^^

It it necessary to provide some configuration before deploying PEDASI.

 1. Tell Ansible to which machine PEDASI should be deployed:

   .. code-block:: none
      :caption: inventory.yml

      [default]
      hostname.domain

 2. Provide required configuration for Django - the required and optional settings are described in :mod:`pedasi.settings`.
    The required settings are:

   .. code-block:: none
      :caption: deploy/.env

      SECRET_KEY=<random string>

      SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=<Google OAuth2 key>
      SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=<Google OAuth2 secret>


Deployment
^^^^^^^^^^

You may now deploy PEDASI using the Ansible provisioning script. If you have set up your Ubuntu instance to use SSH passwordless access, do the following:

.. code-block:: console

   $ ansible-playbook -v -i inventory.yml playbook.yml -u <your_username_on_the_remote_host>

Otherwise, you will need Ansible to prompt for passwords for the remote user and superuser accounts:

.. code-block:: console

   $ ansible-playbook -v -i inventory.yml playbook.yml -u <your_username_on_the_remote_host> -k -K


Post-Deployment
^^^^^^^^^^^^^^^

After deploying PEDASI you must create and activate an initial administrator account:

.. code-block:: console

   $ sudo -s
   $ cd /var/www/pedasi
   $ source env/bin/activate
   $ python manage.py createsuperuser --username <username> --email <email address>


Assigning Data or Application Provider Roles to Accounts 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add Data and/or Application Provider roles to an existing PEDASI User account:

 1. Ensure you are logged in as the PEDASI Administrator account
 2. Go to the administrator pages at https://<server_address>/admin
 3. Select *Users* from the *PROFILES* subsection to display a list of all system users
 4. Select the user account you wish to change, to edit that user's profile
 5. Under the *Groups* section under *Permissions*, select *Data Provider* or *Application Provider* and select the right arrow to add this role to the user's profile
 6. Select *SAVE* at the bottom of the page


Data Providers: Managing Data Sources
-------------------------------------

In order for users to begin using PEDASI, you should provide access to a range of data sources. The following sections will walk you through adding and managing your first data source. We will use the IoTUK Nation Database API (see https://iotuk.org.uk/iotuk-nation-database-api/) as a basic example.

Adding a Data Source
^^^^^^^^^^^^^^^^^^^^

Before adding a new data source, first check if the license type for that data source already exists. Select *Licences* from the navigation bar to display all current licenses, and if the licence you need to use isn't already in the list, you'll need to add it as a new licence type. See *Adding a New Data Source Licence* below.

To add a new data source:

 1. Go to https://<server_address> in a browser, and ensure you are logged in either a Central Administrator or Data Provider-enabled account. If you only have a standard PEDASI User account, you'll need to obtain Data Provider privileges first, so contact the Central Administrator to grant these privileges for your account.
 2. Select *Data Sources* from the PEDASI navigation bar. Then select *New Data Source* from the Data Sources page, and add in details for each of the following fields:

    - *Name*: add in a unique name for this data source, such as 'UKIoT Nations'
    - *Description*: optionally add in some specific details concerning this data source, such as its owner any links or references to any specifications or other documentation regarding the data source and format of the data that is delivered on request, e.g. some of the overview text at https://iotuk.org.uk/projects/iotuk-nation-database%E2%80%8B/ and a link to the page, and perhaps a link to the API details at https://github.com/TheDataCity/IoT-UK-Nation-Database-APIs. If the data source provides partially or fully encrypted data, also specify links to contact information and/or any reference material for obtaining a means to encrypt the data (not required for IoTUK Nations)
    - *Url*: specify the base API URL for this data source, e.g. https://api.iotuk.org.uk/iotOrganisation.
    - *Api key*: optionally specify an API key if one is required for PEDASI to access this resource
    - *Plugin name*: select an appropriate data connector to interface with this API, e.g. DataSetConnector
    - *Licence*: select an appropriate licence from those available in the dropdown list, e.g. Open Database Licence.
    - *Is encrypted*: select this if the data supplied from the data source is partially or fully encrypted, e.g. leave unselected
    - *Public permission level*: see the *Requesting Access to a Data Source* section in the :ref:`User Guide<guide_user>` for a breakdown of the different levels of access you can specify for a data source. e.g. DATA
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
 3. Select *Edit* to edit the data source
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

 1. Select *Licences* from the navigation bar to display all current licenses
 2. Select *New License* to create a new licence
 3. Add detail for the following fields:

    - *Name*: add a full name for a new licence, e.g. Open Database Licence
    - *Short name*: add a short name for the licence, typically an acronym, e.g. ODbL
    - *Version*: add the version number for the licence to use
    - *URL*: add a link to an online resource describing the full terms of the licence

 4. Select 'Create' to create the licence, and you'll be presented with an overview page for that licence.


Approving Data Access Requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Application Providers: Managing Applications
--------------------------------------------


Adding an Application
^^^^^^^^^^^^^^^^^^^^^


Updating an Application
^^^^^^^^^^^^^^^^^^^^^^^


Removing an Application
^^^^^^^^^^^^^^^^^^^^^^^




References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
