.. _guide_developer:

PEDASI Developer Guide
======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. note:: Please read the :ref:`User Guide<guide_user>` first to give you an overview of the PEDASI platform before reading this guide.


Deploying PEDASI for Development
--------------------------------

Overview
^^^^^^^^

A development instance of PEDASI can be automatically deployed using Vagrant. It uses VirtualBox as a virtual machine (VM) management tool to provision a Vagrant-style VM and provisions a PEDASI instance within that VM.


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


Configuration
^^^^^^^^^^^^^

First, check the settings in the *Vagrantfile* in the repository's root directory to ensure any provisioned VM will not conflict with any other resources running on the default ports.

Then create a new *.env* file in the repository's *deploy/* directory with the following contents (replacing *some_test_key* with a string of your choice):

::

   SECRET_KEY=some_test_key
   DEBUG=true


Deployment
^^^^^^^^^^

To deploy the Vagrant instance do the following:

.. code-block:: console

   $ vagrant up


Developing an Application
-------------------------

Obtaining an Application API Key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Code Examples
^^^^^^^^^^^^^


A Basic Example Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^

An `example`_ hosted on GitHub is a lightweight exemplar PEDASI web application that uses the PEDASI Applications API - see the GitHub repository README for more details.

.. _`example`: https://github.com/PEDASI/app-iotorgs-map


Application API Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :ref:`Applications API Reference<ref_applications_api>` documentation covers the API and its endpoints, and how to use it.


Using the Test Suite
^^^^^^^^^^^^^^^^^^^^


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
