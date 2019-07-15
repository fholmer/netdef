Quickstart
==========

Netdef will require a specific project structure:

.. literalinclude:: ../tutorial_first_app/project-structure.txt
   :language: text

Pre made project templates are available using cookiecutter

First install cookiecutter and netdef templates:

.. code-block:: console

    $ pip install cookiecutter
    $ hg clone https://bitbucket.org/fholmer/cookiecutter-netdef

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

Create your first application:

.. code-block:: console

    $ cookiecutter cookiecutter-netdef/cookiecutter-minimal-app

The rest of this documentation assumes that your application is called First-App

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Setup your application
----------------------

Create a virtual environment for your application:

.. code-block:: console

    $ cd First-App
    $ python3 -m venv venv
    $ source venv/bin/activate

Install dependencies:

.. code-block:: console

    $ pip install -r requirements-dev.txt
    $ pip install -r requirements.txt

Link your application into the virtual environment site-packages:

.. code-block:: console

    $ pip install -e .

Create config and log folders for your app:

.. code-block:: console

    $ First-App --init .

Launch application
------------------

There are several ways to run your application.

You can use the the entrypoint:

.. code-block:: console

    $ First-App --run .

Or you can use the package module:

.. code-block:: console

    $ python -m first_app --run .

There is also a simple launcher script:

.. code-block:: console

    $ python launchApp.py

You don't have to activate the virtual environment to run your application. You can run it directly by using absolute paths:

.. code-block:: console

    $ cd /
    $ [insert-abs-path-to-proj]/venv/bin/First-App --run [insert-abs-path-to-proj]

Examples
--------

Create a wheel package:

.. code-block:: console

    $ source venv/bin/activate
    $ python setup.py bdist_wheel
    $ deactivate
 
Deploy to /opt/first_app

.. code-block:: console

    $ mkdir -p /opt/first_app
    $ python3 -m venv /opt/first_app
    $ /opt/first_app/bin/pip install [path-to-first-app-wheel]
    $ /opt/first_app/bin/First-App -i /opt/first_app

Confirm that the application is working:

.. code-block:: console

    $ /opt/first_app/bin/First-App -r /opt/first_app

Create a systemd service unit file:

.. code-block:: ini

    [Unit]
    Description=First-App
    After=syslog.target network-online.target
    
    [Service]
    Type=simple
    User=TODO-INSERT-MY-USERNAME
    Group=TODO-INSERT-MY-USERNAME
    Environment=PYTHONUNBUFFERED=true
    
    WorkingDirectory=/opt/first_app
    ExecStart=/opt/first_app/bin/First-App -r /opt/first_app
    
    StandardOutput=syslog
    StandardError=syslog
    
    [Install]
    WantedBy=multi-user.target


TODO
