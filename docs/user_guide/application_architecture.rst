Application architecture
========================

When you create an application in Netdef, your project package will get
the following structure:

.. code-block:: bash

    /Project-dir
        /proj_package/
            /Controllers
            /Engines
            /Expressions
            /Interfaces
            /Rules
            /Sources

Your application consists of one ``engine``, one or more ``rule``, one or
more ``source`` and one or more ``controller``. The ``engine`` is an instance
of the :class:`netdef.Engines.ThreadedEngine` class, the ``rule`` is an
instance of classes that are inherited from :class:`netdef.Rules.BaseRule`,
``source`` is an instance of classes inherited from
:class:`netdef.Sources.BaseSource`, and ``controller`` is an instance of
classes inherited from :class:`netdef.Controllers.BaseController`. All instances
have their own "inbox" (see :class:`netdef.Shared.SharedQueues.SharedQueues`)
and the instances communicate with each other by registering messages in the
recipient's inbox. The most important message types in your application are
``ADD_SOURCE``, ``ADD_PARSER``, ``WRITE_SOURCE`` and ``RUN_EXPRESSION``.
See :class:`netdef.Shared.SharedQueues.MessageType`

The message flow will in most cases be as follows: *Rules* will
send ``ADD_SOURCE`` to *controllers* at startup. *Controllers* will send
``RUN_EXPRESSION`` back to *rules* on data changes. *Rules* will then
collect *expressions* to be evaluated due to the data change and send
``RUN_EXPRESSION`` to the *engine*. If the *expressions* generate data changes a
``WRITE_SOURCE`` message is sent to *controllers*. 

The example below shows 4 simultaneous controllers and 2 simultaneous rules:

.. image :: ../_static/overview.png

The main task of the application is to:

* Obtain external data using one or more *controllers*.
* Retrieving values ​​from external data and activating *expressions* that
  evaluate the values.
* Transmit data based on the result of the *expression*
