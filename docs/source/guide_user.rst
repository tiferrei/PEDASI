.. _guide_user:

PEDASI User Guide
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


User Model
----------

There are three classes of users within PEDASI:

 - *Basic User*: these are anonymous users, able to browse and search the catalogue's public data sources and associated metadata, and retrieve public datasets from those data sources. They can also request a *PEDASI User* account. The data access activities of Basic Users are not tracked by PEDASI.

 - *PEDASI User*: in addition to what a Basic User can do, these users can also request access to specific data sources, which may be approved by *Data Providers*. These users are also *observed* within PEDASI, with data access activities tracked by the system (for those data sources that opt to track user activities).

Two other types of user types exist for administering PEDASI data sources and applications, that build on what PEDASI Users can do:

 - *Data Provider*: these users may register new data sources within PEDASI, update data sources and their metadata, remove data sources, and approve data source access requests.

 - *Application Provider*: similarly, these users may register new applications within PEDASI, update applications and their metadata, and remove applications.

Applications developed for PEDASI also function as PEDASI Users, having their data access activities optionally tracked within the system, depending on the configuration of data sources.

There is also a PEDASI *Central Administrator* user, able to approve PEDASI User account requests, and assign/remove Data and Application Provider roles to users.


Registering for a PEDASI Account
--------------------------------

The preferred method to register an account with PEDASI is to register your Google account. If you don't have a Google account, you can `sign up for one`_. Once you have an account, you should contact the PEDASI Central Administrator via their contact details and request that your account be added to the system.

Once approved, log in to the system using your Google account by selecting *Google Login* on the front page.

.. _`sign up for one`: https://accounts.google.com/signup


Browsing the Data Catalogue
---------------------------



Viewing data sources
^^^^^^^^^^^^^^^^^^^^

Requesting Access to a Datasource
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the Data Explorer
^^^^^^^^^^^^^^^^^^^^^^^





References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
