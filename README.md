# PEDASI v0.1.0

Developed as a platform and a service to explore research challenges in data security, privacy, and ethics, PEDASI enables providers of data - particularly [Internet of Things](https://en.wikipedia.org/wiki/Internet_of_things) data - to share their data securely within a common catalogue for use by application developers and researchers. Data can either be hosted and made accessible directly within PEDASI as an internal data source, or hosted elsewhere and accessible as an external data source through PEDASI.

An initial deployment of the platform is available at [https://dev.iotobservatory.io].

## Key Features

PEDASI’s key features are:

 - Searchable catalogue of supported data sources registered by data owners
 - Extensible connector interface that currently supports HyperCat and IoTUK Nation Database data sources
 - Dataset discovery and access via a web interface or via an Applications API
 - Queryable and extensible metadata associated with datasets
 - Adoption of W3C PROV-DM specification to track and record dataset creation, update, and access within internal datastore
 - Internally hosted support for read/write NoSQL datastores
 - Functions as a reverse proxy to data sources, returning data from requests exactly as supplied by the data source

## Release Notes

This is a public alpha release, and therefore features and functionality may change and the software and documentation may contain technical bugs or other issues. If you discover any issues please consider registering a [GitHub issue](https://github.com/PEDASI/PEDASI/issues).

## Documentation

Documentation is available on [readthedocs](https://pedasi.readthedocs.io/en/master/) for users, system administrators, data and application providers, and application developers, and is also installed within a PEDASI deployment (e.g. at [https://dev.iotobservatory.io/static/html]).

## Contact Information

 - Project team: Adrian Cox (a.j.cox@soton.ac.uk), Mark Schueler (m.schueler@soton.ac.uk)
 - Development team: James Graham (j.graham@soton.ac.uk), Steve Crouch (s.crouch@ecs.soton.ac.uk)

## Licence

PEDASI is provided under the MIT licence - see the [LICENCE.md](LICENCE.md) file for details.

