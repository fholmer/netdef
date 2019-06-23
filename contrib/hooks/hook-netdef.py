from PyInstaller.utils.hooks import collect_data_files, collect_submodules
datas = collect_data_files("netdef", False, "Engines/templates")
hiddenimports = collect_submodules("netdef")
