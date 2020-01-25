Add a controller
================

Built-in controllers can be activated by adding special values to the config file.

You can look opp the correct :doc:`/api/configs` in API Reference

In this tutorial we will activate the CrontabController and the OPCUAServerController

We will have to merge the two configs into one and add them to ``config/default.conf``

.. code-block:: ini

    [controllers]
    CrontabController = 1
    OPCUAServerController = 1

    [sources]
    CrontabSource = 1
    VariantSource = 1

    [CrontabSource]
    controller = CrontabController

    [VariantSource]
    controller = OPCUAServerController

    [CrontabController]
    [OPCUAServerController]

We also have to merge required packages into ``requirements.txt``:

.. code-block:: text

    crontab
    freeopcua

Next step is to start using the controllers and sources by setting up a Rule.


Add a rule
==========

Built-in rules can be activated by adding special values to the config file,
just like the controllers. There is currently only one built-in rule we can
use.

Add the config for CSVRule to ``config/default.conf`` and replace the example
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


Now you can try to launch the application:

.. code-block:: console

    $ pip install -r requirements.txt
    $ python -m first_app -r .

