.. _guide_user:

PEDASI User Guide
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. include:: release_note.rst


Purpose
-------

This guide is for PEDASI users who want to understand the PEDASI platform and how to use its features.


User Model
----------

There are four classes of users within PEDASI:

 - *Basic User*: these are anonymous users, able to browse and search the catalogue's public data sources and associated metadata and retrieve public datasets from those data sources. They can also request a *PEDASI User* account. The data access activities of Basic Users are not tracked by PEDASI.

 - *PEDASI User*: in addition to what a Basic User can do these users can also request access to specific data sources, which may be approved by *Data Providers*. These users are also *observed* within PEDASI, with data access activities tracked by the system (for those data sources that opt to track user activities).

Another class of user is the *Provider*, used for administering PEDASI data sources and applications. These build on what PEDASI Users can do:

 - *Data Provider*: these users may register new data sources within PEDASI, update data sources and their metadata, remove data sources, and approve data source access requests.

 - *Application Provider*: similarly, these users may register new applications within PEDASI, update applications and their metadata, and remove applications.

Applications developed for PEDASI also function as PEDASI Users, having their data access activities optionally tracked within the system, depending on the configuration of data sources.

There is also a PEDASI *Central Administrator* role, able to approve PEDASI User account requests, and assign/remove Data and Application Provider roles to users.


Obtaining a PEDASI Account
--------------------------

Why Register for an Account?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Registering for an account enables you to be authenticated within the system as a PEDASI User and request access to private data sources and use them if approved.

Data Source Activity Tracking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One of the research aims of PEDASI is to explore research challenges around linkages between data. As such, a PEDASI User's activities in relation to data sources is recorded within the system to assist this research, to determine usage and provenance relationships between datasets across the PEDASI user/application ecosystem, and help inform Data Providers how PEDASI uses their data sources.

As an authenticated PEDASI User, the following data is recorded for each data access for those data sources that opt to record usage data:

 - The date and time of access
 - Your unique PEDASI account reference ID (not your personal Google account details)
 - The type of activity (e.g. access, update, etc.)

These records are held internally within PEDASI and are available to Central Administrators and explicitly approved users (e.g. Data Providers and researchers).


Registering for an Account
^^^^^^^^^^^^^^^^^^^^^^^^^^

The preferred method to register an account with PEDASI is to register your Google account. If you don't have a Google account you can `sign up for one`_. Once you have an account you should contact the PEDASI Central Administrator via their contact details and request that your account be added to the system.

Once approved, log in to the system as a PEDASI User using your Google account by selecting *Google Login* on the front page navigation bar.

.. _`sign up for one`: https://accounts.google.com/signup


Browsing the Data Catalogue
---------------------------

You can view the available data sources within PEDASI by selecting *Data Sources* from the front page navigation bar.


Viewing Data Sources Details
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Selecting *Details* for a data source from the Data Sources page shows the following information:

 - *Owner*: the Data Provider who administers this data source
 - *URL*: a URL to the Application Programming Interface (API) for this data source
 - *Licence*: the licence under which the data is provided. You must ensure you comply with these licensing conditions when using data provided by this data source
 - *Metadata*: additional fields, listed by metadata type, for this data (e.g. data query parameters, etc.)


Requesting Access to a Data Source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're logged in as a PEDASI User (and not anonymously), you may request access to a data source by selecting *Manage Access* from a data source overview page. Note that if you are also an Application Provider, you can also request access to data sources for your applications using this mechanism. From here you can supply the following details for an access request via a form:

 - *User*: the identity of the user or application that is making this request (if making this request on behalf of an application, remember to set this to the identity of the application)
 - *Requested*: The level of access, where a given level also provides access to previous levels:

   - *NONE*: to revoke access to a data source
   - *VIEW*: to view a data source's high-level details
   - *META*: to view a data source's metadata
   - *PROV*: to view a data source's PROV records

 - *Push requested*: to allow the data source to receive updates and/or new data from the user or application, where the data source supports it (currently only internal PEDASI data sources)
 - *Reason*: the reason for the request

The data source's Data Provider will then consider and optionally approve the request. Subsequent requests can be made by the user or Application Provider to either escalate or de-escalate a user's or application's access level, each requiring approval.


Using the Data Explorer
^^^^^^^^^^^^^^^^^^^^^^^

The Data Explorer allows you to explore and obtain data from data sources by building and submitting queries based on that data source's API parameters. This is also intended as an aid for developers who wish to understand and construct PEDASI queries within their applications.

Selecting *Data Explorer* from the data source overview page shows an interface to do this using the following process:

 1. *Select a specific data set if supported*: firstly, if the data source supports multiple data sets, select one from the *Datasets* panel on the bottom right. Dataset-specific metadata will be displayed in the *Metadata* panel on the bottom left.

 2. *Use the Query Builder to construct a query*: in the *Query Builder* panel on the top left, select a query parameter from the dropdown selector (or if they are not configured for this data source, you can add one manually in the *Parameter* field), assign a value to that parameter, and select *Add to Query*. Repeat this as required to build a complete query. You'll be able to see the query that will be sent to PEDASI in the *Query URL* text box as the query is constructed.

 3. *Submit the query and see the results*: select *Submit Query* to submit the query, with the results displayed in the *Query Results* panel on the top right.

Results are presented in the Query Results panel precisely as returned by the data source.


Upgrading an Account to Data and/or Application Provider
--------------------------------------------------------

If you already have a PEDASI User account and would like to add your own data sources or applications to a PEDASI instance, contact the PEDASI site's Central Administrator to obtain these privileges for your account.


References
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
