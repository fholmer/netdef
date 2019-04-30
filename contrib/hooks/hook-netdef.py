import os
import glob

def get_hidden_imports():
    files = glob.glob("*/Rules/*Rule.py")
    files += glob.glob("*/Sources/*Source.py")
    files += glob.glob("*/Controllers/*Controller.py")
    files += glob.glob("*/Engines/webadmin/[!_]*.py")

    return list(".".join( fn.split(os.path.sep) )[:-3] for fn in files)

hiddenimports = get_hidden_imports()

def get_data_list():
    folders = glob.glob("*/Engines/templates")
    folders += glob.glob("*/Engines/templates/admin")
    return list( (os.path.abspath(fn), fn) for fn in folders)

datas = get_data_list()
