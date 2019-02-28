.. _guide_administrator:

PEDASI System Administrator Guide
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :doc:`User Guide<guide_user>` first to give you an overview of the PEDASI platform and how to use its features before reading this guide.


Purpose
-------

This guide is for system administrators wishing to deploy a PEDASI instance, either for production or locally for development.


Production Deployment
---------------------

Overview
^^^^^^^^

A deployment of PEDASI is done automatically to a remote Ubuntu server via a preconfigured Ansible script, which performs the following tasks:

 1. Install prerequisites
 2. Configure databases
 3. Install PEDASI
 4. Configure and start webserver

See the *playbook.yml* Ansible file in the PEDASI repository's root directory for more details.


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


Create Administrator Account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After deploying PEDASI you must create and activate an initial PEDASI Central Administrator account:

.. code-block:: console

   $ sudo -s
   $ cd /var/www/pedasi
   $ source env/bin/activate
   $ python manage.py createsuperuser --username <username> --email <email address>

Once created, you can access your deployment at https://<server_address>.


Assigning Data or Application Provider Roles to Accounts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add Data and/or Application Provider roles to an existing PEDASI User account:

 1. Ensure you are logged in as the PEDASI Central Administrator account
 2. Go to the administrator pages at https://<server_address>/admin
 3. Select *Users* from the *PROFILES* subsection to display a list of all system users
 4. Select the user account you wish to change, to edit that user's profile
 5. Under the *Groups* section under *Permissions*, select *Data Provider* or *Application Provider* and select the right arrow to add this role to the user's profile
 6. Select *SAVE* at the bottom of the page


Development Deployment
----------------------

Overview
^^^^^^^^

A development instance of PEDASI can be automatically and rapidly deployed using Vagrant. It uses VirtualBox as a virtual machine (VM) management tool to provision a Vagrant-style VM and provisions a PEDASI instance within that VM.


Prerequisites
^^^^^^^^^^^^^

Ensure you have the following prerequisites before you begin:

 - A Linux or Mac OS X local machine with the following installed:

   - Vagrant v2.2.0 or above
   - VirtualBox v5.2.0 or above
   - Git command line client v2.0 or above


Cloning the PEDASI Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On your local machine, from a shell first clone the PEDASI repository:

.. code-block:: console

   $ git clone https://github.com/PEDASI/PEDASI.git


Configuring Deployment
^^^^^^^^^^^^^^^^^^^^^^

First, check the settings in the *Vagrantfile* in the repository's root directory to ensure any provisioned VM will not conflict with any other resources running on the default ports.

Then create a new *.env* file in the repository's *deploy/* directory with the following contents (replacing *some_test_key* with a string of your choice):

::

   SECRET_KEY=some_test_key
   DEBUG=true


Managing Deployment
^^^^^^^^^^^^^^^^^^^

To deploy the Vagrant instance, provision the instance, and deploy PEDASI within it, within the PEDASI repository root directory:

.. code-block:: console

   $ vagrant up

The Vagrant instance will now be visible within VirtualBox, and the PEDASI service visible from a browser at http://localhost:8888/.

To access the Vagrant instance from the command line:

.. code-block:: console

   $ vagrant ssh

Please see the `Vagrant documentation`_ for more details on how to use Vagrant, including shutting down and destroying Vagrant instances.

.. _`Vagrant documentation`: https://www.vagrantup.com/docs/


Creating Administrator and Provider Accounts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow the instructions in the *Create Administrator Account* subsection of the *Production Deployment* section above to set up an administrator user, as well as the *Assigning Data or Application Provider Roles to Accounts* subsection if required for other non-administrator users.


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
