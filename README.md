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
clean host running Ubuntu 18.04 LTS, or update an existing PEDASI instance if it was previously deployed with the same script.

To deploy using production settings you must:
* Create an Ansible inventory file and set `production=True` for the machine you wish to deploy to
* Create an SSH key and register it as a deployment key on the PEDASI GitHub project
  * Move the SSH private key file to `deploy/.deployment-key`
* Create a configuration file (see below) `deploy/.env.prod`
* Run the Ansible deployment script `ansible-playbook -v -i inventory.yml playbook.yml -u <remote_username>`


## Configuring PEDASI
Both PEDASI and Django are able to be configured via a `.env` file in the project root.

The required configuration properties are:
- SECRET_KEY - should be a randomly generated value
- DATABASE_USER
- DATABASE_PASSWORD - should be a randomly generated value

Other configuration properties are described at the top of `pedasi/settings.py`.
