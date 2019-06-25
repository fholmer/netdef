from netdef.__main__ import entrypoint

def run_app():
    from . import main

def get_template_config():
    from . import defaultconfig
    return defaultconfig.template_config_string

def cli():
    # entrypoint: console_scripts
    entrypoint(run_app, get_template_config)

if __name__ == '__main__':
    # entrypoint: python -m console_scripts 
    entrypoint(run_app, get_template_config)
