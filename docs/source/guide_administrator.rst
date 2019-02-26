.. _guide_user:

PEDASI Administration Guide
===========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :ref:`User Guide<guide_user>` first to give you an overview of the PEDASI platform before reading this guide.


Deploying PEDASI in Production
------------------------------

A deployment of PEDASI is done automatically to a remote Ubuntu server via a preconfigured Ansible script, which performs the following tasks:

 1. 


Prerequisites
^^^^^^^^^^^^^

Ensure you have the following prerequisites before you begin:

 - Ubuntu 18.04 LTS server with:

   - The latest security updates
   - A static IP address
   - A user account with external SSH access enabled and with sudo access privileges (e.g. 'ubuntu' - ubuntu will be used throughout this documentation) 

 - A Linux or Mac OS X local machine with:

   - Ansible v2.7.1 or above installed
   - Git command line client v2 or above installed


Cloning out the PEDASI Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On your local machine, first clone the PEDASI repository:

.. code-block:: console

   $ git clone https://github.com/PEDASI/PEDASI.git


Configuration
^^^^^^^^^^^^^




Deployment
^^^^^^^^^^


Managing Data Sources
---------------------

Adding a Data Source
^^^^^^^^^^^^^^^^^^^^

Updating a Data Source
^^^^^^^^^^^^^^^^^^^^^^

Removing a Data Source
^^^^^^^^^^^^^^^^^^^^^^

Approving Data Access Requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Managing Applications
---------------------

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
