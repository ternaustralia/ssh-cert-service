
ssh-cert-service
================

TODO: update this !!!!!

Quick intro of project goes here.

Installation
============

.. code:: bash

    pip install ssh_cert_service


Configuration
=============

The application can configured like any other Flask application.

First it will load the bundled `settings.py` file to configure sensible defaults.
Please see `settings.py` and https://terndatateam.bitbucket.io/flask_tern/ for details.

Next it will look for an environment variable `SSH_CERT_SERVICE_SETTINGS`. This environment variable
should point to a python file which will be loaded as well. The format is exactly the same as in `settings.py` .

This project uses ``flask_tern``. Be sure to check documentation https://terndatateam.bitbucket.io/flask_tern/ and code https://bitbucket.org/terndatateam/flask_tern .

Flask-Cors: https://flask-cors.readthedocs.io/en/latest/


Development
===========

Clone the source code and cd into the directory of your local copy.
You may want to adapt settings in .flaskenv

.. code:: bash

    # install project in editable mode
    pip install -e '.[testing,docs]'
    # to run tests use
    pytest
    # coverage report
    pytest --cov --cov-report=html

Build API structure run the following command. Please make sure to install json-refs

.. code:: bash 
    cd src/ssh_cert_service/views/api_v1/api-spec
    bash build.sh



The same can be done within a docker environment. The following is a simple example using alpine.

.. code:: bash

    docker run --rm -it -p 5000:5000 -v "$(pwd)":/ssh_cert_service -w /ssh_cert_service alpine:3.10 sh
    # install python in binary libs in container
    apk add python3 py3-cryptography
    # install pkg in container
    pip3 install -e '.[testing]'
    # run tests inside container
    pytest
    pytest --cov --cov-report=html


Run flask development server.

.. code:: bash

    # locally
    flask run
    # within container
    flask run -h 0.0.0.0

You will have to export two env variables, but one of it is optional. However, before doing this you will need a master_ssh_key, if you don't have it, you can create one with the following command
.. code:: bash
    ssh-keygen -t rsa -C "user_ca" -N "<optiona_passphrese>" -f <path_to_export_keys>/user_ca 

Then, you will need to export the path into an env variable as well as the passphrase if you created it. 
... code:: bash
    export MASTER_PRIVATE_KEY_PATH_ENV=<path_to_export_keys> 
    export MASTER_KEY_PASSPHRASE_ENV=<passphrase> 

The app can then be accessed at http://localhost:5000
