from collections import Iterable
from types import ModuleType
import queue
import logging
from ..Engines.expression.Expression import Expression
from ..Shared.Internal import Statistics
from ..Interfaces.internal.tick import Tick

from ..Sources.BaseSource import BaseSource
from ..Controllers.BaseController import BaseController


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

class BaseRule():
    def __init__(self, name, shared):
        self.name = name
        self.shared = shared
        self.init_queue()
        self.add_interrupt(None)
        self.logger = logging.getLogger("BaseRule")

        # Reference i denne konteksten er en string som identifiserer en kilde
        # altså "source.get_reference()". Dette er altså IKKE id(source)!
        # Hensikten med .get_reference er forklart i Sources/BaseSource.py
        # Hvis du skal ha tak i alle uttrkk som blir berørt av en kilde
        # så bruk "source.get_reference()" som nøkkel i denne her:
        self.search_expression_by_reference = {}

        self.ticks = []

    def add_interrupt(self, interrupt):
        self._interrupt = interrupt

    def has_interrupt(self):
        return self._interrupt.is_set()

    def sleep(self, seconds):
        self._interrupt.wait(seconds)

    def init_queue(self):
        self.incoming = self.shared.queues.get_messages_to_rule(self.name)
        self.messagetypes = self.shared.queues.MessageType

    def loop_incoming(self):
        """ Hoved-loop. sjekker incoming-køen og utfører RUN_EXPRESSION-meldinger
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
        """ Implementer følgende:
              1. Åpne og lese en konfigfil
              2. Opprett SourceInfo for kildene funnet i konfig
              3. Opprett instanse av uttrykk funnet i konfig
              4. Opprett kildeinstanser ut fra data i SourceInfo
              5. Knytt opp kildeinstanse til uttrykk.
              6. Send ADD_SOURCE og ADD_PARSER til kontroller
        """
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
        
    def handle_run_expression(self, incoming):
        raise NotImplementedError

    def add_class_to_controller(self, source_name, controller_name=None):
        """ Sender ADD_PARSER til kontroller. Kontroller bruker disse 
            klassenes statiske funksjoner til å dekode / enkode verdier etc.
            Brukes i parsing av konfigfil.
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
        """ Sender ADD_SOURCE til kontroller.
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
        """ sender RUN_EXPRESSION til motor
        """
        self.shared.queues.run_expressions_in_engine(
            item_instance,
            expressions
        )

    def convert_to_instance(self, item_name, source_name, controller_name, rule_name, defaultvalue):
        """ Bruker kildenavnet til å finne klassen. lager instanse av 
            klassen. returnerer kildeinstansen.
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
        """ Finner alle uttrykkene som er koblet til kilden.
        """
        ref = instance.get_reference()
        if ref in self.search_expression_by_reference:
            return self.search_expression_by_reference[ref]
        else:
            return None

    def rule_name_from_key(self, key, default_rule_name):
        rule = self.shared.config.config(key, "rule", default_rule_name, False)
        if rule == "*":
            return "*"
        if rule in self.shared.queues.available_rules:
            return rule
        raise ValueError("Rule missing for key: {}".format(key))


    def source_and_controller_from_key(self, key, controller=None):
        """ Finner kildenavn og kontrollernavn fra variabelen *key*
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
        """ skriver interessant info til Statistics-singleton
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
        """ det er ikke alltid lett for en kontroller å forstå hva slags
            data som en kilde anser som verdi. Noen kontrollere vet ikke
            hvilken kilde som skal ha dataene engang...
            Men kildeklassen har statiske funksjoner som kontrolleren kan
            bruke til å finne ut av disse tingene!
            Løsningen er at kildeklassen registreres i kontrolleren som
            "parser". Så i denne konteksten er parser og kildeklasse egentlig det
            samme.
        """
        self.add_class_to_controller(source_name, controller_name)

    def add_new_expression(self, expr_info):
        """ Funksjon som gjør litt for mange ting:
              1. Oppdaterer self.search_* funksjonene (indirekte via self.maintain_searches)
              2. Knytter kildene til uttrykket som argumenter
              3. Finner kilder og sender dem til kontroller med ADD_SOURCE
        """
        if not isinstance(expr_info, ExpressionInfo):
            raise TypeError("Expected ExpressionInfo, got %s" % type(expr))

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
                arg = self.get_existing_instance(arg) # erstatt arg med eksisterende instanse

            self.maintain_searches(arg, expr)
            # 2.
            expr.add_arg(arg)
            source_count += 1

            if not already_present:
                arg.register_set_callback(self.shared.queues.write_value_to_controller)
                # 3.
                self.add_instance_to_controller(arg)

        self.shared.expressions.instances.add_expression(expr)

        return source_count

    def maintain_searches(self, source_instance, expression):
        """ Sørger for at self.search_expression_by_reference dict er oppdatert
        """
        source_ref = source_instance.get_reference()

        if source_ref in self.search_expression_by_reference:
            if not expression in self.search_expression_by_reference[source_ref]:
                self.search_expression_by_reference[source_ref].append(expression)
        else:
            self.search_expression_by_reference[source_ref] = [expression]

    def has_existing_instance(self, source_instance):
        """ returnerer True hvis kilden vi jobber med allerede
            finnes. Dette er viktig, for vi ønsker ikke flere
            instanser av en kilde som egentlig refererer til samme
            verdi... 
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
        """ Bare oppdatering av interessant data....
        """
        if Statistics.on:
            ns = self.name + "."
            Statistics.set(ns + "source.references.count", len(self.search_expression_by_reference))
            self.logger.info("Unique sources: %d", len(self.search_expression_by_reference))
            count = 0
            for expressions in self.search_expression_by_reference.values():
                count += len(expressions)
            Statistics.set(ns + "expressions.count", count)
            self.logger.info("expression references: %d", count)


class SourceInfo():
    """ Dette er en dataklasse som *beskriver* en kilde. Regelmotoren
        skal opprette en kildeinstanse basert på denne infoen her.
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
    """ Dette er en dataklasse som *beskriver* et uttrykk. Regelmotoren
        skal opprette et uttrykk basert på denne infoen her.
    """
    __slots__ = ["module", "arguments"]
    def __init__(self, module, arguments, func="expression"):

        if not isinstance(func, str):
            raise TypeError("func: wrong datatype")

        if isinstance(module, Expression):
            self.module = module
        elif isinstance(module, ModuleType):
            self.module = Expression(getattr(module, func), module.__file__)
        else:
            raise TypeError("module: wrong datatype")

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
