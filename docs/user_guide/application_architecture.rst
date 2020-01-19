Application architecture
========================

When you create an application using the Netdef framework your application
consists of:

* Exactly one :term:`engine`.
* At least one :term:`rule`.
* At least one :term:`source`.
* At least one :term:`controller`.
* At least one :term:`expression`.

**Glossary**

.. glossary::

    engine
        The ``engine`` is an instance of 
        :class:`netdef.Engines.ThreadedEngine`.

        .. image :: ../_static/uml/classes_engines.png

    rule
        A ``rule`` is an instance derived from
        :class:`netdef.Rules.BaseRule`.

        .. image :: ../_static/uml/classes_rules.png

    source
        A ``source`` is an instance derived from
        :class:`netdef.Sources.BaseSource`.

        .. image :: ../_static/uml/classes_sources.png

    controller
        A ``controller`` is an instance derived from 
        :class:`netdef.Controllers.BaseController`.

        .. image :: ../_static/uml/classes_controllers.png

    expression
        A python callable that is executed by ``engine`` when a associated
        source changes its value. The associated sources are arguments
        to the callable. See :class:`netdef.Engines.expression.Expression`.

        .. code-block:: python

          # Example:
          def expression(arg1, arg2):
              print("expression was called")
              print("This is a netdef.Engines.expression.Expression.Argument:", arg1)
              print("This is the associated source instance:", arg1.instance)
              print("The name of the associated controller:", arg1.instance.controller)

**Shared queues**

All instances have their own *incoming* queue. This queue is available
to the other instances in the shared object.
See :class:`netdef.Shared.SharedQueues.SharedQueues`

.. image :: ../_static/uml/shared_queues.png

The instances communicate with each other by registering messages in the
recipient's queue. The example below shows a project with one controller
and one rule:

.. image :: ../_static/uml/shared_queues_message_example_1.png

The most important message types in your application are
``APP_STATE``, ``ADD_SOURCE``, ``ADD_PARSER``, ``WRITE_SOURCE`` and
``RUN_EXPRESSION``. See :class:`netdef.Shared.SharedQueues.MessageType`

The message flow will in most cases be as follows:

    At application initialization:

    * The :term:`engine` will send ``APP_STATE`` to all active controllers.
    * Every :term:`rule` will send ``ÀDD_PARSER`` or/and ``ADD_SOURCE``
      to a specific :term:`controller` depending on what is in the configuration
      files.
    * The :term:`engine` will send a new ``APP_STATE`` to all active controllers.

    Repeats until application is terminated:

    * Every :term:`controller` will send ``RUN_EXPRESSION`` back to a specific
      :term:`rule` on data changes.
    * The specific :term:`rule` will then collect the associated
      :term:`expression` to be evaluated depending on given data change and
      send ``RUN_EXPRESSION`` to the :term:`engine`.
    * If the :term:`expression` generate a new data change then a
      ``WRITE_SOURCE`` message is sent back directly to :term:`controller`.


.. seqdiag::

    seqdiag {
        activation = none;
        default_note_color = LemonChiffon;
        span_height = 16;
        edge_length = 140;
        //default_fontsize = 16;

        ThreadedEngine [color=LemonChiffon];
        Rule [color=LemonChiffon];
        Controller [color=LemonChiffon];
        External [shape="flowchart.database"];

        === Initialization ===
        ThreadedEngine -> Controller [label="APP_STATE, AppStateType.SETUP"]
        === Setup ===
        ... Parsing config files ...
        Rule -> Controller [label="ADD_PARSER,\nsource class"]
        Rule -> Controller [label="ADD_SOURCE,\nsource 1"]
        Rule -> Controller [label="ADD_SOURCE,\nsource 2"]
        Rule -> Controller [label="ADD_SOURCE,\nsource [n]"]
        ... Parsing finished ...
        ThreadedEngine -> Controller [label="APP_STATE, AppStateType.RUNNING"]
        === Running ===
        Controller --> External [
          label="
            [optional]
            Setup subscription
            for source [n]"
        ]
        === Begin loop ===
        Controller --> External [label="[optional] Polling"]
        Controller <- External [
          label="Data received",
          leftnote="
            Parses / Unpacks
            external data format
            and updates value of
            source [n]"
        ]
        Controller -> Rule [
          label="RUN_EXPRESSION,\nsource [n]",
          note="
            Value change
            in source [n]"
        ]
        Rule -> ThreadedEngine [
          label="RUN_EXPRESSION,\nexpression [n]",
          note="
            Looks up the expression
            for given source and
            passes it to ThreadedEngine",
          leftnote="
            ThreadedEngine
            Executes expression [n]
            in ThreadPoolExecutor"
        ]
        ... ...
        ThreadedEngine -> Controller [
          label="WRITE_SOURCE, source [n], value, timestamp",
          note="
            If expression
            produces a
            value change"
        ]
        Controller -> External [
          label="Data sent",
          leftnote="
            Packs value into
            external data
            format"
        ]
        === End Loop ===
    }
