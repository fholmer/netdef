Application architecture
========================

Your application consists of:

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

    rule
        A ``rule`` is an instance derived from
        :class:`netdef.Rules.BaseRule`.

    source
        A ``source`` is an instance derived from
        :class:`netdef.Sources.BaseSource`.

    controller
        A ``controller`` is an instance derived from 
        :class:`netdef.Controllers.BaseController`.

    expression
        A python callable that is executed by ``engine`` when a associated
        source changes its value. The associated sources are arguments
        to the callable. See :class:`netdef.Engines.expression.Expression`.

**Shared queues**

All instances have their own *incoming* queue. This queue is available
to the other instances in the shared object.
See :class:`netdef.Shared.SharedQueues.SharedQueues`

.. image :: ../_static/uml/shared_queues.svg

The instances communicate with each other by registering messages in the
recipient's queue. The example below shows a project with one controller
and one rule:

.. image :: ../_static/uml/shared_queues_message_example_1.svg

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

.. image :: ../_static/uml/message_flow_with_external.svg
