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

 1. 


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




Deployment
^^^^^^^^^^


Data Providers: Managing Data Sources
-------------------------------------


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
