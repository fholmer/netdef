Quickstart
==========

Netdef will require a specific project structure:

.. literalinclude:: ../tutorial_first_app/project-structure.txt
   :language: text

Pre made project templates are available using make-project or cookiecutter

Make-project
------------

First install make-project:

.. code-block:: console

    $ python3 -m pip install make

Create your first application:

.. code-block:: console

    $ python3 -m make project gl:fholmer/netdef-project/minimal-app

The rest of this documentation assumes that your application is called First-App


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

You don't have to activate the virtual environment to run your application.
You can run it directly by using absolute paths:

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

.. code-block:: console

    $ sudo /opt/first_app/bin/First-App-Service -u $USER -i /opt/first_app

Confirm that the unit-file looks correct:

.. code-block:: console

    $ cat /etc/systemd/system/first_app.service

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
