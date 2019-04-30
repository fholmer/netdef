from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files("flask_admin", False, "templates")
datas += collect_data_files("flask_admin", False, "static")
