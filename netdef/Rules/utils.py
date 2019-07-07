import importlib
import importlib.util
import sys
import pathlib

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

def get_module_from_string(mod_str, package, abs_root, location_name, mod_name):
    if "/" in mod_str:
        if pathlib.Path(mod_str).is_absolute():
            abs_file = pathlib.Path(mod_str)
        elif abs_root:
            abs_file = pathlib.Path(abs_root).joinpath(mod_str)
        else:
            abs_file = pathlib.Path(mod_str).absolute()
            
        if not abs_file.is_absolute():
            raise ValueError("{} is not absolute path".format(abs_file))
        elif not abs_file.is_file():
            raise ValueError("{} not found".format(abs_file))
        elif not location_name:
            raise ValueError("location_name: expect string, got {}".format(location_name))
        elif not mod_name:
            raise ValueError("mod_name: expect string, got {}".format(mod_name))
        return import_file(mod_str, location_name, mod_name)
    else:
        mod, obj = load_entrypoint(mod_str, package)
        return mod
