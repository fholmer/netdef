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
   :language: text

``setup.py``

* ``package_data``, make sure to include html templates
* ``entry_points``, the entry point will make it easy to launch application

.. literalinclude:: ../tutorial_first_app/setup.py

``first_app/__init__.py``

.. literalinclude:: ../tutorial_first_app/first_app/__init__.py

``first_app/__main__.py``

.. literalinclude:: ../tutorial_first_app/first_app/__main__.py

``first_app/defaultconfig.py``

.. literalinclude:: ../tutorial_first_app/first_app/defaultconfig.py

``first_app/main.py``

.. literalinclude:: ../tutorial_first_app/first_app/main.py

``config/default.conf``

.. literalinclude:: ../tutorial_first_app/config/default.conf
   :language: ini


Add a controller
----------------

Built-in controllers can be activated by adding special values to the config file.

You can look opp the correct :doc:`../api/configs` in API Reference

In this tutorial we will activate the CrontabController and the OPCUAServerController

We will have to merge the two configs into one and add them to ``config/default.conf``

.. code-block:: ini

    [controllers]
    CrontabController = 1
    OPCUAServerController = 1

    [sources]
    CrontabSource = 1
    VariantSource = 1
    BytestringSource = 0

    [CrontabSource]
    controller = CrontabController

    [VariantSource]
    controller = OPCUAServerController

    [BytestringSource]
    controller = OPCUAServerController

    [CrontabController]
    [OPCUAServerController]

Next step is to start using the controllers and sources by setting up a Rule.


Add a rule
----------
Built-in rules can be activated by adding special values to the config file,
just like the controllers. There is currently only one built-in rule we can
use.

Add the config for CSVRule to ``config/default.conf``. But replace the example
rules with a hello_world rule like this:

.. code-block:: ini

    [rules]
    CSVRule = 1

    [CSVRule]
    hello_world_rule = 1

    [hello_world_rule]
    csv = config/hello_world_rule.csv
    py = config/hello_world_rule.py

We now have to create the csv and py file:

``config/hello_world_rule.csv``

.. code-block:: text

    CrontabSource,VariantSource
    */2 * * * * * *,ns=2;s=hello_world


``config/hello_world_rule.py``

.. code-block:: python

    def expression(cron, oua):
        if cron.new:
            oua.set = "Hello, world"

        if cron.update:
            oua.set = "Hello, world {}".format(int(cron.value))


Now you can try to launch the application::

    $ python -m first_app -r .

TODO

Create a custom controller
--------------------------

Copy the included template to create a custom controller.

``netdef/Controllers/NewControllerTemplate.py:``

.. literalinclude:: ../../netdef/Controllers/NewControllerTemplate.py


Paste it into your application with a new name:

``first_app/Controllers/SubprocessController.py:``

..  code-block:: python
    :linenos:
    :emphasize-lines: 7, 9, 10

    import logging
    import datetime
    from netdef.Controllers import BaseController, Controllers
    from netdef.Sources.BaseSource import StatusCode

    # import my supported sources
    from netdef.Sources.NewSourceTemplate import NewSourceTemplate

    @Controllers.register("SubprocessController")
    class SubprocessController(BaseController.BaseController):
        def __init__(self, name, shared):
            super().__init__(name, shared)
    
    ...

Line 9 and 10 is changed to the same name as the file.
Line 7 have to be replaced at a later time to a custom or built-in source

To activate the controller we have to merge following config to ``default.conf``:

.. code-block:: ini

    [controllers]
    SubprocessController = 1

    [SubprocessController]

Result after merge:

.. code-block:: ini

    [controllers]
    CrontabController = 1
    OPCUAServerController = 1
    SubprocessController = 1

    [CrontabController]

    [OPCUAServerController]

    [SubprocessController]

TODO

Create a custom source
----------------------

Copy the included template to create a custom source for your controller.

``netdef/Sources/NewSourceTemplate.py:``

.. literalinclude:: ../../netdef/Sources/NewSourceTemplate.py

Paste it into your application with a new name:

``first_app/Sources/SubprocessSource.py:``

..  code-block:: python
    :linenos:
    :emphasize-lines: 4, 5

    from netdef.Sources import BaseSource, Sources
    from netdef.Interfaces.DefaultInterface import DefaultInterface

    @Sources.register("SubprocessSource")
    class SubprocessSource(BaseSource.BaseSource):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.interface = DefaultInterface
        
        # TODO: add a address for your new controller
        def unpack_address(self):
            return self.key

Line 4 and 5 is changed to the same name as the file.

Change line 7 in your costom controller:

``first_app/Controllers/SubprocessController.py:``

..  code-block:: python
    :linenos:
    :emphasize-lines: 7

    import logging
    import datetime
    from netdef.Controllers import BaseController, Controllers
    from netdef.Sources.BaseSource import StatusCode

    # import my new source
    from ..Sources.SubprocessSource import SubprocessSource
    ...

To activate the source we have to merge following config to ``default.conf``:

.. code-block:: ini

    [sources]
    SubprocessSource = 1

    [SubprocessSource]
    controller = SubprocessController

Result:

.. code-block:: ini

    [controllers]
    CrontabController = 1
    OPCUAServerController = 1
    SubprocessController = 1

    [sources]
    CrontabSource = 1
    VariantSource = 1
    BytestringSource = 0
    SubprocessSource = 1

    [CrontabSource]
    controller = CrontabController

    [VariantSource]
    controller = OPCUAServerController

    [BytestringSource]
    controller = OPCUAServerController

    [SubprocessSource]
    controller = SubprocessController

    [CrontabController]

    [OPCUAServerController]

    [SubprocessController]

TODO

