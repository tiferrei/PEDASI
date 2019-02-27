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

 1. Install prerequisites
 2. Configure databases
 3. Install PEDASI
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

   $ ansible-playbook -v -i inventory.yml playbook.yml -u <your username on the remote host>

Otherwise, you will need Ansible to prompt for passwords for the remote user and superuser accounts:

.. code-block:: console

   $ ansible-playbook -v -i inventory.yml playbook.yml -u <your username on the remote host> -k -K


Post-Deployment
^^^^^^^^^^^^^^^

After deploying PEDASI you must create and activate an initial administrator account:

.. code-block:: console

   $ sudo -s
   $ cd /var/www/pedasi
   $ source env/bin/activate
   $ python manage.py createsuperuser --username <username> --email <email address>


Data Providers: Managing Data Sources
-------------------------------------

In order for users to begin using PEDASI, you should provide access to a range of data sources. The following sections will walk you through adding and managing your first data source. We will use the IoTUK Nation Database API (see https://iotuk.org.uk/iotuk-nation-database-api/) as a basic example.

Adding a Data Source
^^^^^^^^^^^^^^^^^^^^



Updating a Data Source
^^^^^^^^^^^^^^^^^^^^^^


Removing a Data Source
^^^^^^^^^^^^^^^^^^^^^^


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
