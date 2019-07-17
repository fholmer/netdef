.. highlight:: shell

============
Installation
============

Netdef is implemented in `Python`__ and supports Python 3.5.3+.

__ https://docs.python-guide.org/


Debian
------

Prerequisites::

    # python 3.5 +
    $ sudo apt-get install python3 python3-pip python3-venv

    # requirements for building psutil
    $ sudo apt-get install build-essential python3-dev

Create an Virtual environment::

    $ python3 -m venv venv

Activate the environment::

    $ source venv/bin/activate

Install Netdef::

    $ pip install netdef


Windows
-------

Prerequisites:

Get `Python`__

__ https://www.python.org/downloads/windows/

Create an Virtual environment::

    py -3 -m venv venv

Activate the environment::

    venv\Scripts\activate

Install Netdef::

    pip install netdef


