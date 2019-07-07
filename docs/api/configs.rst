Built-in configs
==================

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
    example-data-as-int,example-data-as-text

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
            key:    example-data-as-int

          - source: TextSource
            key:    example-data-as-text

.. code-block:: python
   :caption: config/example_rule_101.py

    def setup(shared):
        pass

    def expression(intdata, textdata):
        pass
