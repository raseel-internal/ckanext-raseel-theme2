# Raseel Open Data Platform

![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-informational?style=flat-square)

**Homepage:**

## Maintainers

| Name             | Email               | Url |
| ---------------- | ------------------- | --- |
| Meriam Bouaouaja | <mbo@softifi.com>   |     |
| Hossam Badri     | <hbadri@mda.gov.sa> |     |

# Requirements

This extension is compatible with CKAN 2.8 and higher.

# Installation

To install ckanext-raseel-theme:

1.  Activate your CKAN virtual environment, for example:

        . /usr/lib/ckan/default/bin/activate

2.  Install the package into your virtual environment:

        pip install ckanext-raseel_theme2

3.  Add `raseel_theme` to the `ckan.plugins` setting in your CKAN
    config file (by default the config file is located at
    `/etc/ckan/default/production.ini`).

4.  Restart CKAN. For example if you've deployed CKAN with Apache on
    Ubuntu:

        sudo service apache2 reload

# Development Installation

To install ckanext-raseel-theme for development, activate your CKAN
virtualenv and do:

    git clone https://github.com/raseel/ckanext-raseel-theme2.git
    cd ckanext-raseel-theme2
    python setup.py develop
    pip install -r dev-requirements.txt

# Translations

In development mode, just do

    python setup.py extract_messages
    python setup.py update_catalog --locale ar
    python setup.py compile_catalog --locale ar

if you are working on docker container you should first get in the container

      docker-compose exec ckan bash
      cd /srv/app/src/ckanext-raseel-theme2

For more setup, just follow instructions here: <https://docs.ckan.org/en/2.8/extensions/translating-extensions.html>
(you need a working installation of CKAN and an active virtualenv for it to work).
