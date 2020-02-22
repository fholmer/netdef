Netdef
======

* Documentation: https://netdef.readthedocs.io/en/latest/
* GitHub: https://github.com/fholmer/netdef
* GitLab: https://gitlab.com/fholmer/netdef
* PyPI: https://pypi.org/project/netdef/
* License: GNU Lesser General Public License v3 or later (LGPLv3+)

Summary
-------

An application framework with built-in drivers (Controllers),
data holders (Sources) and config parsers (Rules).
Also includes a web interface for configuration and troubleshooting.

Features
--------

* Abstract base classes for creating custom controllers, sources and rules
* The configuration is done using configparser with extended interpolation
* Start a new netdef project with
  `cookiecutter <https://pypi.org/project/cookiecutter>`_ or
  `make-project <https://pypi.org/project/make>`_.
  Templates available at https://gitlab.com/fholmer/netdef-project/
* Built-in Controllers:

  * OpcUa server / client (`freeopcua <https://pypi.org/project/opcua>`_)
  * TcpModbus server / client (`pymodbus <https://pypi.org/project/pymodbus>`_)
  * icmp ping / url ping
  * XmlRpc client
  * trigger events by using crontab format
    (`crontab <https://pypi.org/project/crontab>`_)
  * disk, memory and CPU monitoring
    (`psutil <https://pypi.org/project/psutil>`_)
  * MQTT client (using a simple messaging format called
    `DataMessage <https://gitlab.com/fholmer/netdef/-/blob/master/netdef/Interfaces/datamessage/datamessage.py>`_)
    (`paho-mqtt <https://pypi.org/project/paho-mqtt>`_)
  * Simple RESTJson client
  * Simple Influxdb logger (`influxdb <https://pypi.org/project/influxdb>`_)

* Built-in Rules:

  * Generic CSV config parser
  * Generic INI config parser
  * Generic Yaml config parser (`PyYAML <https://pypi.org/project/PyYAML>`_)

* Built-in application engines:

  * threaded engine with stdout/stderr only
  * threaded engine with web-interface (webadmin)
  * serve webadmin behind nginx reverse proxy

Use Cases
---------

Netdef is useful if you want to create a middleware that can translate a
protocol into a completely different protocol or data format into a completely
different data format.

Getting started
---------------

First install make-project::

    $ python3 -m pip install --user make

Create your first application::

    $ python3 -m make project gl:fholmer/netdef-project/minimal-app

When asked for *project_name* type *Test-App*::

    project_name? [First-App]: Test-App

Setup development environment for your application::

    $ cd Test-App
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install wheel
    $ pip install -r requirements-dev.txt
    $ pip install -r requirements.txt
    $ python -m test_app -i .

Run::

    $ python -m test_app -r .

*CTRL-C* to exit

Package your application::

    $ python setup.py bdist_wheel

Exit development environment::

    $ deactivate

Prepare deployment::

    $ sudo mkdir -p /opt/test-app
    $ sudo chown $USER:$USER /opt/test-app/
    $ python3 -m venv /opt/test-app/

Deploy your application::

    $ source /opt/test-app/bin/activate
    $ pip install ./dist/Test_App-0.1.0-py3-none-any.whl
    $ python -m test_app -i /opt/test-app/

Install as service::

    $ sudo /opt/test-app/bin/Test-App-Service -u $USER --install /opt/test-app/

Enable and run::

    $ sudo systemctl --system daemon-reload
    $ sudo systemctl enable test-app-service.service
    $ sudo systemctl start test-app-service.service
