import importlib
import functools
import logging
from collections import OrderedDict

VIEWDICT = OrderedDict()

def register(name):
    def classdecorator(name, cls):
        VIEWDICT[name] = cls
        return cls
    return functools.partial(classdecorator, name)

class Views():
    def __init__(self, shared=None):
        self.items = VIEWDICT
        self.add_shared_object(shared)
        self.logging = logging.getLogger(__name__)
        
    def add_shared_object(self, shared):
        self.shared = shared

    def load(self, base_packages):

        if isinstance(base_packages, str):
            base_packages = [base_packages]
        
        added = []

        #insert default webadmin views into configfile
        activate_views = OrderedDict()
        activate_views["FileModel"] = 1
        activate_views["SettingsModel"] = 1
        activate_views["SourcesModel"] = 1
        activate_views["ExpressionsView"] = 1
        activate_views["StatisticsModel"] = 1
        activate_views["Tools"] = 1
        activate_views.update(self.shared.config.get_dict("webadmin_views"))

        for name, activate in activate_views.items():
            for base_package in base_packages:
                if int(activate) and not name in added:
                    try:
                        importlib.import_module("{}.Engines.webadmin.{}".format(base_package, name))
                        added.append(name)
                    except ImportError as err:
                        if isinstance(err.name, str):
                            if not err.name.startswith("{}.Engines.webadmin".format(base_package)):
                                if not err.name == "{}.Engines".format(base_package):
                                    raise(err)
                        else:
                            raise(err)

        for name, activate in activate_views.items():
            if int(activate) and not name in added:
                self.logging.error("%s not found in %s", name, base_packages)

    def setup(self, admin):
        for setup in self.items.values():
            setup(admin)
