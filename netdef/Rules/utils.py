import importlib
import importlib.util
import sys

V_MAJOR = sys.version_info.major
V_MINOR = sys.version_info.minor

# function to import module from anywere
if V_MAJOR == 3 and V_MINOR > 4:

    def import_file(abs_pyfile, location_name, mod_name):
        #py 3.5+
        spec = importlib.util.spec_from_file_location(
            "%s.%s" % (location_name, mod_name),
            abs_pyfile)

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        return mod
else:

    from importlib.machinery import SourceFileLoader

    def import_file(abs_pyfile, location_name, mod_name):
        #py 3.4:
        mod_string = "%s.%s" % (location_name, mod_name)
        mod = SourceFileLoader(mod_string, abs_pyfile).load_module()
        return mod

def load_entrypoint(entrypoint, package=None):
    modname, qualname_separator, qualname = entrypoint.partition(':')
    mod = importlib.import_module(modname, package)
    obj = None
    if qualname_separator:
        for attr in qualname.split('.'):
            obj = getattr(mod, attr)
    return mod, obj
