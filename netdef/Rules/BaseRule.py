from collections import Iterable
from types import ModuleType
import queue
import logging
from ..Engines.expression.Expression import Expression
from ..Shared.Internal import Statistics
from ..Interfaces.internal.tick import Tick
from ..Sources.BaseSource import BaseSource
from ..Controllers.BaseController import BaseController
from .utils import get_module_from_string


# Det er en blanding av norsk og engelsk her.
#
# Alle kommentarer er på norsk, men all *kode* er engelsk og
# bruker engelske navn.
#
# ORDBOK for å lese kommentarer:
# kilde = source
# kontroller = controller
# uttrykk = expression
# regelmotor = rule
# motor = threadedengine
#

# Reference in this context is a string that identifies a source
# "source.get_reference()". This is NOT the same as id(source)!
# The purpose of .get_reference is explained in Sources / BaseSource.py
# If you want to get hold of all expressions affected by a source
# then you can use "source.get_reference ()".


class BaseRule():
    """
    Abstract class for rules.

    :param str name: Name to be used in logfiles
    :param netdef.Shared.Shared shared: a reference to the shared object
    """
    def __init__(self, name, shared):
        self.name = name
        self.shared = shared
        self.init_queue()
        self.add_interrupt(None)
        self.logger = logging.getLogger("BaseRule")
        
        self.stats_unique_sources = 0
        self.stats_unique_expressions = 0

        self.ticks = []

        self._expressions_setup_functions = []

    def add_interrupt(self, interrupt):
        "Setup the interrupt signal"
        self._interrupt = interrupt

    def has_interrupt(self):
        "Returns True if the interrupt signal is received"
        return self._interrupt.is_set()

    def sleep(self, seconds):
        """"
        Sleep by waiting for the interrupt.
        Should be used instead of time.sleep.
        Override if sleep should be interrupted by even more signals
        """
        self._interrupt.wait(seconds)

    def init_queue(self):
        "Setup the message queue and timeout"
        self.incoming = self.shared.queues.get_messages_to_rule(self.name)
        self.messagetypes = self.shared.queues.MessageType

    def loop_incoming(self):
        """ Get every message from the queue and dispatch the associated handler function
        """
        try:
            while not self.has_interrupt():
                if Statistics.on:
                    Statistics.set(self.name + ".incoming.count", self.incoming.qsize())
                messagetype, incoming = self.incoming.get(block=True, timeout=0.1)
                if messagetype == self.messagetypes.RUN_EXPRESSION:
                    self.handle_run_expression(incoming)
                else:
                    raise NotImplementedError
        except queue.Empty:
            pass

    def setup(self):
        """
        Implement the following:
        
            1. Open and read a configuration file
            2. Create SourceInfo for the sources found in config
            3. Create instance of expression found in config
            4. Create source instances based on data in SourceInfo
            5. Link source instances to expression.
            6. Send ADD_SOURCE and ADD_PARSER to controllers
        """
        raise NotImplementedError


    def run(self):
        """
        Override this function in rule. Example:

        .. code-block:: python

            def run(self):
                self.logger.info("Running")

                while not self.has_interrupt():
                    self.loop_incoming() # dispatch handle_* functions

                self.logger.info("Stopped")

        """
        raise NotImplementedError
        
    def handle_run_expression(self, incoming):
        raise NotImplementedError

    def add_class_to_controller(self, source_name, controller_name=None):
        """
        Sends ADD_PARSER to controls. Controllers will use static functions
        defined in these classes to decode / encode values etc.

        :param str source_name: source name as string
        :param str controller_name: controller name as string

        """

        if not controller_name:
            controller_name = self.source_and_controller_from_key(source_name)[1]

        source_class = self.shared.sources.classes.get_item(source_name)
        self.shared.queues.send_message_to_controller(
            self.shared.queues.MessageType.ADD_PARSER,
            controller_name,
            source_class
        )

    def add_instance_to_controller(self, item_instance):
        """ Send ADD_SOURCE to controller of given source.

            :param netdef.Sources.BaseSource item_instance: source instance

        """
        try:
            self.shared.sources.instances.add_item(item_instance)

            self.shared.queues.send_message_to_controller(
                self.shared.queues.MessageType.ADD_SOURCE,
                item_instance.controller,
                item_instance
            )

        except Exception as eee:
            self.logger.exception(eee)

    def send_expressions_to_engine(self, item_instance, expressions):
        """ Send RUN_EXPRESSION to the engine

        :param item_instance: the source instance that triggered the expressions
        :param list expressions: list of expressions

        """
        self.shared.queues.run_expressions_in_engine(
            item_instance,
            expressions
        )

    def convert_to_instance(self, item_name, source_name, controller_name, rule_name, defaultvalue):
        """
        Uses the source name to find the actual source class.
        Make a instance off the given source class, returns the instance
        
        :param str item_name: item as string
        :param str source_name: source as string
        :param str controller_name: controller as string
        :param str rule_name: rule as string
        :param defaultvalue: could be anything.

        :returns: instance of source

        """

        source_class = self.shared.sources.classes.get_item(source_name)

        item_instance = source_class(
            rule=rule_name,
            controller=controller_name,
            source=source_name,
            key=item_name,
            value=defaultvalue
            )
        return item_instance

    def get_expressions(self, instance):
        """ 
        Returns all expression that is associated with the given instance

        :returns: list or None
        """

        ref = instance.get_reference()
        shared_expr = self.shared.expressions.instances

        if shared_expr.has_source_ref(ref):
            return shared_expr.get_expressions_by_source_ref(ref)
        else:
            return None

    def rule_name_from_key(self, key, default_rule_name):
        """
        Check if rule name is valid.

        :param str key: the source key
        :param str default_rule_name: rule name to use if not found by given key
        :returns: rule name
        :rtype: str
        :raises ValueError: if rule does not exists

        """
        rule = self.shared.config.config(key, "rule", default_rule_name, False)
        if rule in self.shared.queues.available_rules:
            return rule
        raise ValueError("Rule missing for key: {}".format(key))


    def source_and_controller_from_key(self, key, controller=None):
        """
        Check if controller name is valid.
        Returns a valid (key, controller) tuple

        :param str key: the source key
        :param str controller: controller name to use if not found by given key
        :returns: tuple of key and controller
        :rtype: tuple
        :raises ValueError: if controller does not exists

        """

        available_controllers = self.shared.queues.available_controllers
        available_sources = self.shared.sources.classes.items
        if key in available_sources:
            if controller:
                if controller in available_controllers:
                    return key, controller
            else:
                controller = self.shared.config.config(key, "controller", "", False)
                if controller in available_controllers:
                    return key, controller
        raise ValueError("Controller {} missing for key: {}".format(controller, key))

    def update_statistics(self, namespace, error_count, expression_count, source_count):
        """ Write useful info to Statistics-singleton
        """
        if Statistics.on:
            ns = namespace + "."
            Statistics.set(ns + "expression.error.count", error_count)
            self.logger.info(ns + "Parsed expression failures: %d", error_count)
            Statistics.set(ns + "expression.count", expression_count)
            self.logger.info(ns + "Parsed expressions: %d", expression_count)
            Statistics.set(ns + "source.count", source_count)
            self.logger.info(ns + "Parsed sources: %d", source_count)

    def add_new_parser(self, source_name, controller_name=None):
        """
        It is not always easy for a controller to understand what kind
        data that a source regards as value. Some controllers do not even know
        which source to update with data.
        
        Therefore the source classes has static functions that the controller can
        use to find out these things.

        Use this function to add a source class to a controller as a parser.

        :param str source_name: source as string
        :param str controller_name: controller as string

        """
        self.add_class_to_controller(source_name, controller_name)

    @staticmethod
    def get_module_from_string(mod_str, package=None, abs_root=None, location_name=None, mod_name=None):
        return get_module_from_string(mod_str, package, abs_root, location_name, mod_name)

    def add_new_expression(self, expr_info):
        """
        This function does too many things:

        1. Updates shared.expressions.instances (indirectly via self.maintain_searches)
        2. Associate the sources with expressions as arguments
        3. Finds sources and sends them to controllers with ADD_SOURCE message
        """

        if not isinstance(expr_info, ExpressionInfo):
            raise TypeError("Expected ExpressionInfo, got %s" % type(expr_info))

        source_count = 0
        expr = expr_info.module
       
        for sourceinfo in expr_info.arguments:
            if not isinstance(sourceinfo, SourceInfo):
                raise TypeError("Expected SourceInfo, got %s" % type(sourceinfo))

            source_name, controller_name = self.source_and_controller_from_key(
                sourceinfo.typename, sourceinfo.controller)
            
            rule_name = self.rule_name_from_key(sourceinfo.typename, self.name)
            defaultvalue = sourceinfo.defaultvalue

            arg = self.convert_to_instance(sourceinfo.key, source_name, controller_name, rule_name, defaultvalue)
            # 1.
            already_present = self.has_existing_instance(arg)
            if already_present:
                arg = self.get_existing_instance(arg) # replace arg with existing instance

            self.maintain_searches(arg, expr)
            # 2.
            expr.add_arg(arg)
            source_count += 1

            if not already_present:
                arg.register_set_callback(self.shared.queues.write_value_to_controller)
                # 3.
                self.add_instance_to_controller(arg)

        if expr_info.setup and not expr_info.setup in self._expressions_setup_functions:
            self._expressions_setup_functions.append(expr_info.setup)
            expr_info.setup(self.shared)

        self.shared.expressions.instances.add_expression(expr)

        return source_count

    def maintain_searches(self, source_instance, expression):
        """ Keeps shared.expressions.instances updated
        """
        source_ref = source_instance.get_reference()
        shared_expr = self.shared.expressions.instances

        if shared_expr.has_source_ref(source_ref):
            if not shared_expr.has_expression_in_source_ref(source_ref, expression):
                self.stats_unique_expressions += 1
                shared_expr.add_expression_in_source_ref(source_ref, expression)
        else:
            self.stats_unique_sources += 1
            self.stats_unique_expressions += 1
            shared_expr.add_expression_in_source_ref(source_ref, expression)

    def has_existing_instance(self, source_instance):
        """
        Returns True if the source we are working on already
        exists. This is important, because we do not want more
        than one source instance for each value...
        """

        return self.shared.sources.instances.has_item_ref(source_instance.get_reference())
        
    def get_existing_instance(self, source_instance):
        return self.shared.sources.instances.get_item_by_ref(source_instance.get_reference())

    def setup_ticks(self):
        self.ticks = [Tick(c) for c in self.shared.queues.available_controllers]

    def send_ticks(self):
        for tick in self.ticks:
            self.shared.queues.send_message_to_controller(
                self.shared.queues.MessageType.TICK,
                tick.controller,
                tick
            )

    def get_ticks(self):
        return self.ticks

    def process_ticks(self):
        if Statistics.on:
            for tick in self.get_ticks():
                Statistics.set("{}.ticks.timediff".format(tick.controller), tick.timediff())


    def setup_done(self):
        "Update useful statistics"

        self._expressions_setup_functions.clear()
        if Statistics.on:
            ns = self.name + "."
            Statistics.set(ns + "source.references.count", self.stats_unique_sources)
            self.logger.info("Unique sources: %d", self.stats_unique_sources)
            Statistics.set(ns + "expressions.count", self.stats_unique_expressions)
            self.logger.info("expression references: %d", self.stats_unique_expressions)


class SourceInfo():
    """ This is a data class that *describes* a source. The rule
        shall create a source instance based on this *description*
    """

    __slots__ = ["typename", "key", "controller", "defaultvalue"]
    def __init__(self, typename, key, controller=None, defaultvalue=None):
        self.key = key
        self.defaultvalue = defaultvalue

        if isinstance(typename, str):
            self.typename = typename
        else:
            raise TypeError("typename: wrong datatype: {}".format(typename))

        if controller is None:
            self.controller = None
        elif isinstance(controller, str):
            self.controller = controller
        elif isinstance(controller, BaseController):
            self.controller = controller.name
        else:
            raise TypeError("controller: wrong datatype")

class ExpressionInfo():
    """ This is a data class that *describes* an expression. The rule
        shall create an expression  based on this *description*
    """

    __slots__ = ["module", "func", "arguments", "setup"]
    def __init__(self, module, arguments, func="expression", setup="setup"):

        if not isinstance(func, str):
            raise TypeError("func: wrong datatype")

        if isinstance(module, Expression):
            _pymod = None
            _expr = module
        elif isinstance(module, ModuleType):
            _pymod = module
            _expr = Expression(getattr(_pymod, func), _pymod.__file__)
        else:
            raise TypeError("module: wrong datatype")

        self.module = _expr

        if setup and hasattr(_pymod, setup):
            self.setup = getattr(_pymod, setup)
        else:
            self.setup = None

        self.arguments = []
        if not arguments:
            raise ValueError("arguments: empty")

        elif isinstance(arguments, Iterable):
            for arg in arguments:
                if isinstance(arg, SourceInfo):
                    self.arguments.append(arg)
                else:
                    raise TypeError("arguments: not SourceInfo")
        elif isinstance(arguments, SourceInfo):
            self.arguments.append(arguments)

        else:
            raise ValueError("arguments: not a list of SourceInfo")
