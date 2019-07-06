Netdef
======

* Documentation: https://netdef.readthedocs.io/en/latest/
* Bitbucket: https://bitbucket.org/fholmer/netdef
* GitHub: https://github.com/fholmer/netdef
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
* Start a new netdef project with cookiecutter. Templates available at https://bitbucket.org/fholmer/cookiecutter-netdef.

Built-in Controllers:

* OpcUa server / client ([freeopcua](https://pypi.org/project/freeopcua/))
* TcpModbus server / client ([pymodbus](https://pypi.org/project/pymodbus/))
* icmp ping / url ping
* XmlRpc client
* trigger events by using crontab format ([crontab](https://pypi.org/project/crontab/))
* disk, memory and CPU monitoring ([psutil](https://pypi.org/project/psutil/))
* MQTT client (using a simple messaging format called DataAccess) ([paho-mqtt](https://pypi.org/project/paho-mqtt/))
* Simple RESTJson client

Built-in Rules:

* Generic CSV config parser

Built-in application engines:

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

First install cookiecutter and netdef templates::

    $ python3 -m venv cookiecutter/
    $ cookiecutter/bin/pip install cookiecutter
    $ hg clone https://bitbucket.org/fholmer/cookiecutter-netdef cookiecutter/cookiecutter-netdef

Create your first application::

    $ cookiecutter/bin/cookiecutter cookiecutter/cookiecutter-netdef/cookiecutter-minimal-app

Cookiecutter and netdef-templates can now be removed if you wish.

Setup your application::

    $ cd your-application
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements-dev.txt
    $ pip install -r requirements.txt
