Built-in configs
==================

.. contents::
   :depth: 3
   :local:

Controller configs
------------------

CommTestController
++++++++++++++++++
.. literalinclude:: ../controller-configs/CommTestController.conf
   :language: ini
   :caption: config/default.conf


ModbusServerController
++++++++++++++++++++++
.. literalinclude:: ../controller-configs/ModbusServerController.conf
   :language: ini
   :caption: config/default.conf


NewControllerTemplate
+++++++++++++++++++++
.. literalinclude:: ../controller-configs/NewControllerTemplate.conf
   :language: ini
   :caption: config/default.conf


SystemMonitorController
+++++++++++++++++++++++
.. literalinclude:: ../controller-configs/SystemMonitorController.conf
   :language: ini
   :caption: config/default.conf


ZmqDataAccessController
+++++++++++++++++++++++
.. literalinclude:: ../controller-configs/ZmqDataAccessController.conf
   :language: ini
   :caption: config/default.conf


CrontabController
+++++++++++++++++
.. literalinclude:: ../controller-configs/CrontabController.conf
   :language: ini
   :caption: config/default.conf


MQTTDataAccessController
++++++++++++++++++++++++
.. literalinclude:: ../controller-configs/MQTTDataAccessController.conf
   :language: ini
   :caption: config/default.conf


OPCUAServerController
+++++++++++++++++++++
.. literalinclude:: ../controller-configs/OPCUAServerController.conf
   :language: ini
   :caption: config/default.conf


XmlRpcController
++++++++++++++++
.. literalinclude:: ../controller-configs/XmlRpcController.conf
   :language: ini
   :caption: config/default.conf

ConcurrentWebRequestController
++++++++++++++++++++++++++++++
.. literalinclude:: ../controller-configs/ConcurrentWebRequestController.conf
   :language: ini
   :caption: config/default.conf

InfluxDBLoggerController
++++++++++++++++++++++++
.. literalinclude:: ../controller-configs/InfluxDBLogger.conf
   :language: ini
   :caption: config/default.conf


Rule configs
------------

CSVRule
+++++++

.. literalinclude:: ../rule-configs/CSVRule.conf
   :language: ini
   :caption: config/default.conf

.. code-block:: text
   :caption: config/example_rule_101.csv

    IntegerSource,TextSource
    example-data1-as-int,example-data1-as-text
    example-data2-as-int,example-data2-as-text

.. code-block:: python
   :caption: config/example_rule_101.py

    def setup(shared):
        pass

    def expression(intdata, textdata):
        pass


YAMLRule
++++++++

.. literalinclude:: ../rule-configs/YAMLRule.conf
   :language: ini
   :caption: config/default.conf

.. code-block:: yaml
   :caption: config/example_rule_101.yaml

    parsers: 
      - source: IntegerSource
      - source: TextSource

    expressions:
      - module: config/example_rule_101.py
        setup: setup
        expression: expression
        arguments:
          - source: IntegerSource
            key:    example-data1-as-int

          - source: TextSource
            key:    example-data1-as-text

      - module: config/example_rule_101.py
        setup: setup
        expression: expression
        arguments:
          - source: IntegerSource
            key:    example-data2-as-int

          - source: TextSource
            key:    example-data2-as-text

.. code-block:: python
   :caption: config/example_rule_101.py

    def setup(shared):
        pass

    def expression(intdata, textdata):
        pass


INIRule
++++++++

.. literalinclude:: ../rule-configs/INIRule.conf
   :language: ini
   :caption: config/default.conf

.. code-block:: ini
   :caption: config/example_rule_101.ini

    [example_rule_101]
    on = 1
    parsers = IntegerSource, TextSource
    module = config/example_rule_101.py
    setup = setup
    expression = expression
    arguments:
        IntegerSource(example-data1-as-int), TextSource(example-data1-as-text)
        IntegerSource(example-data2-as-int), TextSource(example-data2-as-text)

.. code-block:: python
   :caption: config/example_rule_101.py

    def setup(shared):
        pass

    def expression(intdata, textdata):
        pass

InfluxDBLoggerRule
++++++++++++++++++

.. literalinclude:: ../rule-configs/InfluxDBLogger.conf
   :language: ini
   :caption: config/default.conf
