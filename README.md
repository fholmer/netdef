
netdef
======

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

* Abstract BaseController-class to create custom controllers
* Abstract BaseSource-class to create custom sources
* Abstract BaseRule-class to create custom sources
* Config files with interpolation support
* Start a new netdef project with cookiecutter. Templates available at https://bitbucket.org/fholmer/cookiecutter-netdef.
* Code in Rule-Source-Controller design pattern.

Built-in Controllers:

* OpcUa server / client
* TcpModbus server / client
* icmp ping / url ping
* XmlRpc client
* trigger events by using crontab format
* System monitoring
* MQTT client (using a simple messaging format called DataAccess)
* ZeroMQ client (using a simple messaging format called DataAccess)
* Simple RESTJson client

Built-in Rules:

* CSV config parser

Built-in application engines:

* threaded engine with stdout/stderr only
* threaded engine with web-interface (webadmin)
* serve webadmin behind nginx reverse proxy

Use Cases
---------

Netdef is useful if:

* You need to transform data in protocol into a completly different protocol
* You need to transform a data-format into a completly different data-format

Getting started
---------------

First install cookiecutter and netdef templates:

    $ python3 -m venv cookiecutter/
    $ cookiecutter/bin/pip install cookiecutter
    $ hg clone https://bitbucket.org/fholmer/cookiecutter-netdef cookiecutter/cookiecutter-netdef

Create your first application:

    $ cookiecutter/bin/cookiecutter cookiecutter/cookiecutter-netdef/cookiecutter-minimal-app
