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

Deploying PEDASI for Development
--------------------------------

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


Developing an Application
-------------------------

The following sections will walk you through using the PEDASI Applications API in your own applications. We will use the JavaScript IoTUK Nation Map Demo application (see https://github.com/Southampton-RSG/app-iotorgs-map) as a basic example. These instructions assume you are aiming to develop against a production deployment of PEDASI managed buy a Central Administrator, but you can also use a local development deployment if you wish.

Adding Required Data Sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Firstly, you'll need to ensure that the data sources your application aims to use are added to PEDASI, which require Data Provider account privileges. If you do not already have these privileges on your PEDASI account, either:

 - Contact your local PEDASI Data Provider to register the data sources
 - Contact the PEDASI Central Administrator to register the data sources
 - Contact the PEDASI Central Administrator to request Data Provider privileges for your account

If you now have these privileges and wish to add the data sources yourself, follow the *Adding a Data Source* section in the :doc:`Data and Application Provider Guide<guide_provider>` (which also contains details for adding the IoTUK Nation Data as a data source).


Obtaining an Application API Key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will first need to register some basic application details to obtain an API key for your application to authenticate with PEDASI, which requires Application Provider account privileges. If you do not have these privileges on your PEDASI account, either:

 - Contact your local PEDASI Application Provider to register the application and obtain an API key
 - Contact the PEDASI Central Administrator to register the new application and obtain an API key
 - Contact the PEDASI Central Administrator to request Application Provider privileges for your account

If you now have these privileges and wish to add the application yourself, follow the *Adding an Application* section in the :doc:`Data and Application Provider Guide<guide_provider>` (which also contains details for adding the IoTUK Nation Map Demo application).


Code Examples
^^^^^^^^^^^^^




A Basic Example Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^

An `example`_ hosted on GitHub is a lightweight exemplar PEDASI web application that uses the PEDASI Applications API - see the GitHub repository README for more details.

.. _`example`: https://github.com/PEDASI/app-iotorgs-map


Application API Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :doc:`Applications API Reference<ref_applications_api>` documentation covers the API and its endpoints, and how to use it.


Using the Test Suite
^^^^^^^^^^^^^^^^^^^^


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
