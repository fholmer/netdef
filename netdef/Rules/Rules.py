import logging
import importlib
import functools

RULESDICT = {}

def register(name):
    def classdecorator(name, cls):
        RULESDICT[name] = cls
        return cls
    return functools.partial(classdecorator, name)


class Rules():
    def __init__(self, shared=None):
        self.classes = RULESDICT
        self.instances = {}
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
                        importlib.import_module("{}.Rules.{}".format(base_package, name))
                        self.shared.queues.add_rule(name)
                        added.append(name)
                    except ImportError as e:
                        if isinstance(e.name, str):
                            if not e.name.startswith(base_package + ".Rules"):
                                raise(e)
                        else:
                            raise(e)

        for name, activate in activate_rules.items():
            if int(activate) and not name in added:
                self.logging.error("%s not found in %s", name, base_packages)
