Create a custom controller
==========================

Copy the included template to create a custom controller.

``netdef/Controllers/NewControllerTemplate.py``:

.. literalinclude:: /../netdef/Controllers/NewControllerTemplate.py


Paste it into your application with a new name:

``first_app/Controllers/CmdController.py``:

.. code-block:: python
    :linenos:
    :emphasize-lines: 7, 9, 10

    import logging
    import datetime
    from netdef.Controllers import BaseController, Controllers
    from netdef.Sources.BaseSource import StatusCode

    # import my supported sources
    from netdef.Sources.NewSourceTemplate import NewSourceTemplate

    @Controllers.register("CmdController")
    class CmdController(BaseController.BaseController):
        def __init__(self, name, shared):
            super().__init__(name, shared)
    
    ...

Line 9 and 10 is changed to the same name as the file.
Line 7 have to be replaced at a later time to a custom or built-in source

To activate the controller we have to merge following config to ``default.conf``:

.. code-block:: ini

    [controllers]
    CmdController = 1

    [CmdController]

Result after merge:

.. code-block:: ini

    [controllers]
    CrontabController = 1
    OPCUAServerController = 1
    CmdController = 1

    [CrontabController]

    [OPCUAServerController]

    [CmdController]


Create a custom source
======================

Copy the included template to create a custom source for your controller.

``netdef/Sources/NewSourceTemplate.py``:

.. literalinclude:: /../netdef/Sources/NewSourceTemplate.py

Paste it into your application with a new name:

``first_app/Sources/CmdSource.py``:

.. code-block:: python
    :linenos:
    :emphasize-lines: 4, 5

    from netdef.Sources import BaseSource, Sources
    from netdef.Interfaces.DefaultInterface import DefaultInterface

    @Sources.register("CmdSource")
    class CmdSource(BaseSource.BaseSource):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.interface = DefaultInterface
        
        # TODO: add a address for your new controller
        def unpack_address(self):
            return self.key

Line 4 and 5 is changed to the same name as the file.

Change line 7 in your custom controller:

``first_app/Controllers/CmdController.py``:

.. code-block:: python
    :linenos:
    :emphasize-lines: 7

    import logging
    import datetime
    from netdef.Controllers import BaseController, Controllers
    from netdef.Sources.BaseSource import StatusCode

    # import my new source
    from ..Sources.CmdSource import CmdSource
    ...

To activate the source we have to merge following config to ``default.conf``:

.. code-block:: ini

    [sources]
    CmdSource = 1

    [CmdSource]
    controller = CmdController

Result:

.. code-block:: ini

    [controllers]
    CrontabController = 1
    OPCUAServerController = 1
    CmdController = 1

    [sources]
    CrontabSource = 1
    VariantSource = 1
    CmdSource = 1

    [CrontabSource]
    controller = CrontabController

    [VariantSource]
    controller = OPCUAServerController

    [CmdSource]
    controller = CmdController

    [CrontabController]

    [OPCUAServerController]

    [CmdController]


Create a custom rule
====================

Copy the included template to create a custom rule.

``netdef/Rules/NewRuleTemplate.py``:

.. literalinclude:: /../netdef/Rules/NewRuleTemplate.py

Paste it into your application with a new name:

``first_app/Rules/FirstAppRule.py``:

.. code-block:: python
    :linenos:
    :emphasize-lines: 9, 10

    import logging
    import pathlib
    from .utils import import_file
    from . import BaseRule, Rules

    SourceInfo = BaseRule.SourceInfo
    ExpressionInfo = BaseRule.ExpressionInfo

    @Rules.register("FirstAppRule")
    class FirstAppRule(BaseRule.BaseRule):
        def __init__(self, name, shared):
            super().__init__(name, shared)
            self.logger = logging.getLogger(name)
            self.logger.info("init")

Line 9 and 10 is changed to the same name as the file.

To activate the rule we have to merge following config to ``default.conf``:

.. code-block:: ini

    [rules]
    FirstAppRule = 1

    [FirstAppRule]

Result:

.. code-block:: ini

    [rules]
    FirstAppRule = 1

    [FirstAppRule]

    [controllers]
    CrontabController = 1
    OPCUAServerController = 1
    CmdController = 1

    [sources]
    CrontabSource = 1
    VariantSource = 1
    CmdSource = 1

    [CrontabSource]
    controller = CrontabController

    [VariantSource]
    controller = OPCUAServerController

    [CmdSource]
    controller = CmdController

    [CrontabController]

    [OPCUAServerController]

    [CmdController]
