import functools
import importlib
import logging
from collections import OrderedDict

RULESDICT = OrderedDict()


def register(name, classref=None):
    """
    A decorator to register rules. Example::

        from netdef.Rules import BaseRule, Rules

        @Rules.register("NewRuleTemplate")
        class NewRuleTemplate(BaseRule.BaseRule):
            def __init__(self, name, shared):
                ...
    
    Can also be called as a normal function::

        from netdef.Rules import BaseRule, Rules

        def setup(shared):
            Rules.register("NewRuleTemplate", NewRuleTemplate)

        class NewRuleTemplate(BaseRule.BaseRule):
            def __init__(self, name, shared):
                ...

    :param str name: Name of the rule class
    :param object classref: Should be *None* if used as a decorator and
                            a *class* if called as a function
    
    :return: A callable that returns a *class* if used as a decorator
             and a *class* if called as a normal function

    """

    def classdecorator(name, cls):
        RULESDICT[name] = cls
        return cls

    # if register is called as a normal function with two arguments
    if not classref is None:
        return classdecorator(name, classref)

    # if register is called as a decorator with one argument
    return functools.partial(classdecorator, name)


class Rules:
    def __init__(self, shared=None):
        self.classes = RULESDICT
        self.instances = OrderedDict()
        self.add_shared_object(shared)
        self.logging = logging.getLogger(__name__)

    def add_shared_object(self, shared):
        self.shared = shared

    def init(self):
        for name, class_ in self.classes.items():
            self.instances[name] = class_(name, self.shared)

    def load(self, base_packages):

        if isinstance(base_packages, str):
            base_packages = [base_packages]

        added = []

        activate_rules = self.shared.config.get_dict("rules")

        for base_package in base_packages:
            for name, activate in activate_rules.items():
                if int(activate) and not name in added:
                    try:
                        _mod = importlib.import_module(
                            "{}.Rules.{}".format(base_package, name)
                        )
                        added.append(name)
                        if hasattr(_mod, "setup"):
                            getattr(_mod, "setup")(self.shared)

                    except ImportError as e:
                        if isinstance(e.name, str):
                            if not e.name.startswith(base_package + ".Rules"):
                                raise (e)
                        else:
                            raise (e)

        for name, activate in activate_rules.items():
            if int(activate) and not name in added:
                self.logging.error("%s not found in %s", name, base_packages)

        for name in self.classes.keys():
            self.shared.queues.add_rule(name)
