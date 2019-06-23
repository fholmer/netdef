.. highlight:: shell

Build from source
=================

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

    $ hg clone https://fholmer@bitbucket.org/fholmer/netdef
    $ cd netdef

Setup virtual environment:

.. code-block:: console

    $ python3 -m venv venv
    $ source venv/bin/activate

Build sdist and wheel:

.. code-block:: console

    $ python setup.py sdist
    $ python setup.py bdist_wheel


Windows 10
++++++++++

Install requirements:

You have to install `Python`_ and `Mercurial`_

Get sources:

.. code-block:: console

    hg clone https://fholmer@bitbucket.org/fholmer/netdef
    cd netdef

Setup virtual environment:

.. code-block:: console

    py -3 -m venv venv
    venv\Scripts\activate

Build sdist and wheel

.. code-block:: console

    python setup.py sdist
    python setup.py bdist_wheel


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
    $ apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended latexmk

Setup virtual environment:

.. code-block:: console

    $ python3 -m venv venv
    $ source venv/bin/activate

Build docs:

.. code-block:: console

    $ cd docs
    $ make html
    $ make latexpdf
