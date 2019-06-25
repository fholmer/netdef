========
Tutorial
========

Project layout
--------------

create a Project folder::

    $ mkdir First-App
    $ cd First-App

    $ mkdir config
    $ mkdir log
    $ mkdir first_app

* ``First-App``, The Project name.
* ``config``, applications default configfiles
* ``log``, application.log is created in this folder
* ``first_app``, the python package with your applications files

.. literalinclude:: ../tutorial_first_app/project-structure.txt

``setup.py``

.. literalinclude:: ../tutorial_first_app/setup.py

``first_app/__init__.py``

.. literalinclude:: ../tutorial_first_app/first_app/__init__.py

``first_app/__main__.py``

.. literalinclude:: ../tutorial_first_app/first_app/__main__.py

``first_app/defaultconfig.py``

.. literalinclude:: ../tutorial_first_app/first_app/defaultconfig.py

``first_app/main.py``

.. literalinclude:: ../tutorial_first_app/first_app/main.py

TODO
