import functools
import importlib
import logging
from collections import OrderedDict

SOURCEDICT = OrderedDict()


def register(name, classref=None):
    """
    A decorator to register sources. Example::

        from netdef.Sources import BaseSource, Sources

        @Sources.register("NewSourceTemplate")
        class NewSourceTemplate(BaseSource.BaseSource):
            def __init__(self, name, shared):
                ...
    
    Can also be called as a normal function::

        from netdef.Sources import BaseSource, Sources

        def setup(shared):
            Sources.register("NewSourceTemplate", NewSourceTemplate)

        class NewSourceTemplate(BaseSource.BaseSource):
            def __init__(self, name, shared):
                ...

    :param str name: Name of the source class
    :param object classref: Should be *None* if used as a decorator and
                            a *class* if called as a function
    
    :return: A callable that returns a *class* if used as a decorator
             and a *class* if called as a normal function

    """
    def classdecorator(name, cls):
        SOURCEDICT[name] = cls
        return cls

    #if register is called as a normal function with two arguments
    if not classref is None:
        return classdecorator(name, classref)
    
    #if register is called as a decorator with one argument
    return functools.partial(classdecorator, name)


class Sources:
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
                        _mod = importlib.import_module(
                            "{}.Sources.{}".format(base_package, name)
                        )
                        added.append(name)
                        if hasattr(_mod, "setup"):
                            getattr(_mod, "setup")(self.shared)

                    except ImportError as e:
                        if isinstance(e.name, str):
                            if not e.name.startswith(base_package + ".Sources"):
                                raise (e)
                        else:
                            raise (e)

        for name, activate in activate_sources.items():
            if int(activate) and not name in added:
                self.logging.error("%s not found in %s", name, base_packages)

        activate_aliases = self.shared.config.get_dict("source_aliases")
        for name, origin in activate_aliases.items():
            if origin in self.items:
                self.items[name] = self.items[origin]
            else:
                self.logging.error(
                    "%s not found for alias %s in configfile", origin, name
                )
