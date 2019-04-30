import importlib
import functools
import logging

CONTROLLERDICT = {}

# denne dekoratoren vil bli aktivert av aktiverte klasser etter Controllers.load()
def register(name):
    def classdecorator(name, cls):
        CONTROLLERDICT[name] = cls
        return cls
    return functools.partial(classdecorator, name)

class Controllers():
    def __init__(self, shared=None):
        self.logging = logging.getLogger(__name__)
        self.items = CONTROLLERDICT
        self.add_shared_object(shared)
        self.instances = {}

    def add_shared_object(self, shared):
        self.shared = shared

    def init(self):
        for name, class_ in self.items.items():
            self.instances[name] = class_(name, self.shared)

    def load(self, base_packages):
        """ Importerer controller-modulene. lager kø-instanser til controllermodulene
            Gjør forberedelser slik at alle delte klasser og instanser er "på plass"
            når instansen av kontrolleren senere blir initiert
        """
        if isinstance(base_packages, str):
            base_packages = [base_packages]
        
        added = []

        for base_package in base_packages:

            activate_controllers = self.shared.config.get_dict("controllers")
            for name, activate in activate_controllers.items():
                if int(activate) and not name in added:
                    try:
                        # laster modul
                        importlib.import_module("{}.Controllers.{}".format(base_package, name))
                        # lager kø-instanser
                        added.append(name)
                        self.shared.queues.add_controller(name)
                    except ImportError as e:
                        if isinstance(e.name, str):
                            if not e.name.startswith(base_package + ".Controllers"):
                                raise(e)
                        else:
                            raise(e)

        for name, activate in activate_controllers.items():
            if int(activate) and not name in added:
                    self.logging.error("%s not found in %s", name, base_packages)

        activate_aliases = self.shared.config.get_dict("controller_aliases")
        for name, origin in activate_aliases.items():
            if origin in self.items:
                self.items[name] = self.items[origin]
                self.shared.queues.add_controller(name)
            else:
                self.logging.error("%s not found for alias %s in configfile", origin, name)