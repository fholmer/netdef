import importlib
import functools
import logging

SOURCEDICT = {}

def register(name):
    def classdecorator(name, cls):
        SOURCEDICT[name] = cls
        return cls
    return functools.partial(classdecorator, name)

class Sources():
    def __init__(self, shared=None):
        self.items = SOURCEDICT
        self.add_shared_object(shared)
        self.logging = logging.getLogger(__name__)

    def add_shared_object(self, shared):
        self.shared = shared

    def init(self):
        for source_name, class_ in self.items.items():
            self.shared.sources.classes.add_item(source_name, class_)

    def load(self, base_packages):

        if isinstance(base_packages, str):
            base_packages = [base_packages]
        
        activate_sources = self.shared.config.get_dict("sources")
        added = []

        for base_package in base_packages:
            for name, activate in activate_sources.items():
                if int(activate) and not name in added:
                    try:
                        importlib.import_module("{}.Sources.{}".format(base_package, name))
                        added.append(name)
                    except ImportError as e:
                        if isinstance(e.name, str):
                            if not e.name.startswith(base_package + ".Sources"):
                                raise(e)
                        else:
                            raise(e)

        for name, activate in activate_sources.items():
            if int(activate) and not name in added:
                self.logging.error("%s not found in %s", name, base_packages)

        activate_aliases = self.shared.config.get_dict("source_aliases")
        for name, origin in activate_aliases.items():
            if origin in self.items:
                self.items[name] = self.items[origin]
            else:
                self.logging.error("%s not found for alias %s in configfile", origin, name)
