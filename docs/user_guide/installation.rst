============
Installation
============

Netdef is implemented in `Python`__ and supports Python 3.5.3+.

__ https://docs.python-guide.org/


**Prerequisites**

  * Debian:

    Python3 requirements can be installed by typing:

    .. code-block:: console

        $ sudo apt-get install python3 python3-pip python3-venv

    Requirements for building psutil:
    
    .. code-block:: console

        $ sudo apt-get install build-essential python3-dev

    Ensure you have installed python 3.5.3 or newer.
    You can check this by typing:

    .. code-block:: console

        $ python3 -V
        Python 3.5.3

  * Windows:
  
    Ensure you have installed Python 3.5.3 or newer.
    You can check this by opening command prompt and type:

    .. code-block:: doscon

        > py -3 -V
        Python 3.5.3
    
    If ``py.exe`` is not found then you have to download and install
    `Python <https://www.python.org/downloads/windows/>`_ 3.5.3 or newer.


**Create an Virtual environment**

  * Linux:

    .. code-block:: console

        $ python3 -m venv venv

  * Windows:

    .. code-block:: doscon

        > py -3 -m venv venv


**Activate the environment**

  * Linux:

    .. code-block:: console

        $ source venv/bin/activate

  * Windows:


    .. code-block:: doscon

        > venv\Scripts\activate


**Install Netdef**

  * Linux:

    .. code-block:: console

        $ pip install netdef

  * Windows:

    .. code-block:: doscon

        > pip install netdef
