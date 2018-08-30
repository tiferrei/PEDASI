# PEDASI

PEDASI is an Internet of Things (IoT) Observatory demonstrator platform.

It functions as middleware between data sources and applications to provide a testbed for investigation of
research questions in the domain of IoT.


## Running / Deploying PEDASI

### In Development
To run PEDASI locally during development you will need to install and run:

* MySQL server
  * Create a schema to hold the PEDASI core database tables
* MongoDB server
  * Create a database to hold the PEDASI PROV collections

It is recommended that you then create a Python virtual environment in which to run PEDASI.
The Python requirements are described in the `requirements.txt` file.

PEDASI can be run using the Django development server by `python manage.py runserver`.

### In Production

This repository contains an Ansible `playbook.yml` file which will perform a full install of PEDASI onto a
clean host, or update an existing PEDASI instance if it was previously deployed with the same script.

To deploy using production settings you must create an Ansible inventory file and set `production=True` for
the machine you wish to deploy to.


## Configuring PEDASI
Both PEDASI and Django are able to be configured via a `.env` file in the project root.

The only required configuration property is the Django SECRET_KEY which should be a randomly generated
character sequence.

Other configuration properties are described at the top of `pedasi/settings.py`.
