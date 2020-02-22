.. highlight:: shell

Build from source
=================

Python
------

Normally you don't have to compile python. On Windows you can download 
pre-compiled binaries, and most linux distros have a pre-installed version
of python.

Compiling to a relative directory:

.. code-block:: console

    $ mkdir ~/Python-3.8/
    $ cd ~/Python-3.8/
    $ wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz
    $ tar zxvf Python-3.8.1.tgz
    $ Python-3.8.1/configure
    $ make
    $ make install DESTDIR=.

Or absolute directory:

.. code-block:: console

    $ mkdir /opt/Python-3.8/
    $ cd /opt/Python-3.8/
    $ wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz
    $ tar zxvf Python-3.8.1.tgz
    $ Python-3.8.1/configure --prefix=/opt/Python-3.8
    $ make
    $ make install



psutil
------

Normally you don't have to compile yourself. ``pip install`` should compile
automatically. If automatic compilation fails you can try to specify
include dirs and library dirs:

.. code-block:: console

    $ pip install --global-option=build_ext \
      --global-option="-I~/Python-3.8/usr/local/include/python3.8" \
      --global-option="-L~/Python-3.8/usr/local/lib" \
      psutil

Netdef package
--------------

Debian
++++++

Install requirements:

.. code-block:: console

    # python 3.5 +
    $ sudo apt-get install python3 python3-pip python3-venv

    # source control management
    $ sudo apt-get mercurial

    # requirements for building psutil
    $ sudo apt-get install build-essential python3-dev

Get sources:

.. code-block:: console

    $ hg clone git+ssh://git@gitlab.com:fholmer/netdef.git
    $ cd netdef

Setup virtual environment:

.. code-block:: console

    $ python3 -m venv venv
    $ source venv/bin/activate

Build sdist and wheel:

.. code-block:: console

    $ python setup.py sdist
    $ python setup.py bdist_wheel


Windows
+++++++

Install requirements:

Get `Python`_ and `Mercurial`_

Get sources:

.. code-block:: doscon

    > hg clone git+ssh://git@gitlab.com:fholmer/netdef.git
    > cd netdef

Setup an virtual environment:

.. code-block:: doscon

    > py -3 -m venv venv
    > venv\Scripts\activate

Build sdist and wheel

.. code-block:: doscon

    > python setup.py sdist
    > python setup.py bdist_wheel


.. _Python: https://www.python.org/downloads/windows/
.. _Mercurial: https://www.mercurial-scm.org/

Docs
----

Debian
++++++

Install requirements

.. code-block:: console

    # requirements for building psutil
    $ sudo apt-get install build-essential python3-dev

    # requirements for pdf
    $ sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended latexmk

    # requirements for pdf multi language
    $ sudo apt-get install texlive-lang-european texlive-lang-english

    # requirements for UML diagram
    $ sudo apt-get install plantuml

Setup virtual environment:

.. code-block:: console

    $ python3 -m venv venv
    $ source venv/bin/activate

Build docs:

.. code-block:: console

    $ cd docs
    $ make html
    $ make latexpdf


UML diagrams:

.. note::

    This is only needed if UML diagrams is out of date:
    
    .. code-block:: console
    
        $ plantuml -tsvg docs/_static/uml/
