Putting it all together
-----------------------

In this example we want to pass following commands to the subprocess module:

* echo hello
* ls -lah .
* ./simple_script.sh
* echo Don\'t break the

We could hard code these commands in the controller but it is more flexible
to create a source for each command. And we also want to read these commands
from a config file so it will be easy to reuse, change or extend the commands.

To achieve this we just implement a method in the source that returns the
command. the command can be extracted from the sources key:

``first_app/Sources/SubprocessSource.py``:

.. code-block:: python
    :linenos:

    from netdef.Sources import BaseSource, Sources
    from netdef.Interfaces.DefaultInterface import DefaultInterface

    @Sources.register("SubprocessSource")
    class SubprocessSource(BaseSource.BaseSource):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.interface = DefaultInterface

        def get_command_and_args(self, args=None):
            if args:
                return self.key + " " + args
            else:
                return self.key

The controller can retrieve the command to run by calling
:attr:`get_command_and_args` 

``first_app/Controllers/SubprocessController.py``:

.. code-block:: python
    :lineno-start: 1

    import logging
    import datetime
    import subprocess
    import shlex

    from netdef.Controllers import BaseController, Controllers
    from netdef.Sources.BaseSource import StatusCode

    from ..Sources.SubprocessSource import SubprocessSource

We will use subprocess and shlex from standard library to execute commands.
To keep it simple we can create a wrapper function that run a command and
return the result from stdout. In case of error the function return the error
as text instead. Also, charset decoding errors is replaced with "?".

.. code-block:: python
    :lineno-start: 10

    def stdout_from_terminal(command_as_str, err_msg=None):
        command_args = shlex.split(command_as_str)
        try:
            res = subprocess.run(command_args, stdout=subprocess.PIPE).stdout
            return str(res, errors="replace")
        except Exception as error:
            if err_msg is None:
                return str(error)
            else:
                return err_msg

We create an option ``value_as_args`` to use the value from the source to be
added as an argument to the command. the option is read from config file.

.. code-block:: python
    :lineno-start: 20

    @Controllers.register("SubprocessController")
    class SubprocessController(BaseController.BaseController):
        def __init__(self, name, shared):
            super().__init__(name, shared)
            self.logger = logging.getLogger(self.name)
            self.logger.info("init")
            self.value_as_args = self.shared.config.config(self.name, "value_as_args", 1)

The run method will be very simple in this tutorial.
Normally this is where we create a polling loop or setup subscriptions
and await events. In this example we only wait for WRITE_SOURCE messages.
So we only have to iterate the message queue:

.. code-block:: python
    :lineno-start: 27

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # dispatch handle_* functions
        self.logger.info("Stopped")

The rule will always send the source instance at startup as a
ADD_SOURCE message. we have to receive the message and keep it
in our controller. We can use 
:attr:`netdef.Controllers.BaseController.BaseController.add_source`

.. code-block:: python
    :lineno-start: 33

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

When an expression changes the value on one of our sources we will receive
a WRITE_SOURCE message. We have to verify that the received source is in
our source list and that we know how to handle it.

To check if it is one of ours we use
:attr:`netdef.Controllers.BaseController.BaseController.has_source`

To check if we know how to handle it we check if it is an instance of
the source we created :class:`SubprocessSource`.

.. code-block:: python
    :lineno-start: 36

    def handle_write_source(self, incoming, value, source_time):
        self.logger.debug("'Write source' event to %s. value: %s at: %s", incoming.key, value, source_time)
        if not self.has_source(incoming.key):
            self.logger.error(
                "%s not found",
                incoming.key
                )
            return

        if not isinstance(incoming, SubprocessSource):
            self.logger.error(
                "Got write event for %s, but only SubprocessSource is supported",
                type(incoming)
                )
            return

We have verified that the source is an instance of :class:`SubprocessSource`.
Knowing this we can safely call :attr:`SubprocessSource.get_command_and_args`
to get the command.

.. code-block:: python
    :lineno-start: 51

        if self.value_as_args:
            cmd_as_str = incoming.get_command_and_args(value)
        else:
            cmd_as_str = incoming.get_command_and_args()

        new_val = stdout_from_terminal(cmd_as_str)
        stime = datetime.datetime.utcnow()
        status_ok = True # Why not
        cmp_oldew = False # compare old and new value?

At last we create and send a RUN_EXPRESSION message using
:attr:`netdef.Controllers.BaseController.BaseController.update_source_instance_value`
and :attr:`netdef.Controllers.BaseController.BaseController.send_outgoing`

.. code-block:: python
    :lineno-start: 60

        if self.update_source_instance_value(incoming, new_val, stime, status_ok, cmp_oldew):
            self.send_outgoing(incoming)

We now have to create the configfile and expression that is parsed by rule.
The command list can be a simple text file:

``config/command_rule.txt``:

.. code-block:: text
    :lineno-start: 1

    echo hello
    ls -lah .
    ./simple_script.sh
    echo Don\'t break the

The expression is a python file. The rule expect to find a function called :func:`expression`

``config/command_rule.py``:

.. code-block:: python
    :lineno-start: 1

    import logging
    logger = logging.getLogger(__name__ + ":expression")

    def expression(intern, cmd):
        # triggers at startup
        if intern.new:

            if "hello" in cmd.key:
                arg = "world"
            elif "Don\\'t break the" in cmd.key:
                arg = "circle"
            else:
                arg = ""

            logger.info("{}: Send command arg: {}".format(cmd.key, arg))
            cmd.set = arg
        
        if cmd.new or cmd.update:
            logger.info("{}: Result: {}".format(cmd.key, cmd.value))



Now we are ready to create the rule

``first_app/Rules/FirstAppRule.py``:

.. code-block:: python
    :lineno-start: 1

    import logging
    import pathlib
    from netdef.Rules.utils import import_file
    from netdef.Rules import BaseRule, Rules

    SourceInfo = BaseRule.SourceInfo
    ExpressionInfo = BaseRule.ExpressionInfo

We will look for the config file and expression file relative to the project
folder.

.. code-block:: python
    :lineno-start: 8

    @Rules.register("FirstAppRule")
    class FirstAppRule(BaseRule.BaseRule):
        def __init__(self, name, shared):
            super().__init__(name, shared)
            self.logger = logging.getLogger(name)
            self.logger.info("init")
            self.proj_path = shared.config.config("proj", "path")

        def read_list(self, rel_file):
            full_file = pathlib.Path(self.proj_path).joinpath(rel_file)
            lines = open(str(full_file), "r").readlines() 
            return [l.strip() for l in lines]

        def import_py_file(self, rel_file):
            full_file = pathlib.Path(self.proj_path).joinpath(rel_file)
            nice_name = full_file.name
            return import_file(str(full_file), self.name, nice_name)

TODO

.. code-block:: python
    :lineno-start: 25

        def setup(self):
            self.logger.info("Running setup")
            self.setup_commands()
            self.logger.info("Done parsing")

        def setup_commands(self):
            command_expression_module = self.import_py_file("config/command_rule.py")
            command_list = self.read_list("config/command_rule.txt")

            source_count = 0
            for command in command_list:
                source_count += self.add_new_expression(
                    ExpressionInfo(
                        command_expression_module,
                        [
                            SourceInfo("InternalSource", "generic"),
                            SourceInfo("SubprocessSource", command)
                        ]
                    )
                )
            self.update_statistics(self.name + ".commands", 0, 1, source_count)

TODO

.. code-block:: python
    :lineno-start: 46

        def run(self):
            self.logger.info("Running")
            while not self.has_interrupt():
                self.loop_incoming() #  dispatch handle_* functions
            self.logger.info("Stopped")

TODO

.. code-block:: python
    :lineno-start: 51

        def handle_run_expression(self, incoming):
            expressions = self.get_expressions(incoming)
            self.logger.debug("Received %s. Found expressions %s",incoming.key, len(expressions))
            if expressions:
                self.send_expressions_to_engine(incoming, expressions)

TODO


``config/default.ini``

.. code-block:: ini
    :linenos:

    [rules]
    FirstAppRule = 1

    [FirstAppRule]

    [sources]
    SubprocessSource = 1
    InternalSource = 1

    [SubprocessSource]
    controller = SubprocessController

    [InternalSource]
    controller = InternalController

    [controllers]
    SubprocessController = 1
    InternalController = 1

    [InternalController]
    send_init_event = 1

    [SubprocessController]
    value_as_args = 1
