from argparse import ArgumentParser
import getpass
import pathlib
import os

def run_app():
    from . import main

def get_template_config():
    from . import defaultconfig
    return defaultconfig.template_config_string

def entrypoint(run_callback, template_config_callback):
    """
    Entrypoint to be used in your application. Parses Command line arguments
    and dispatch functions.

    Example from ``First-App/first_app/__main__.py``::

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

    """

    global_parser = ArgumentParser(add_help=True)
    global_parser.add_argument('proj_path', type=pathlib.Path, help='path to project directory')
    global_parser.add_argument('-i', '--init', action='store_true', help='setup project directory')
    global_parser.add_argument('-ga', '--generate-auth', action='store_true', help='generate webadmin authentication')
    global_parser.add_argument('-gc', '--generate-certificate', action='store_true', help='generate ssl certificate')
    global_parser.add_argument('-r', '--run', action='store_true', help='start application')
    args = global_parser.parse_args()

    proj_path = args.proj_path.expanduser().absolute()
    os.chdir(str(proj_path))

    if args.init:
        create_project(proj_path, template_config_callback)
    elif args.generate_auth:
        generate_webadmin_auth()
    elif args.generate_certificate:
        generate_certificate()
    elif args.run:
        run_callback()
    else:
        print("Proj path: {}".format(proj_path))
        print("use argument -r, --run to start application")

def create_project(proj_path, template_config_callback):
    """
    Create project structure in given folder. Add content from
    `template_config_callback` into ``config/default.ini``

    :param str proj_path: project folder
    :param str template_config_callback: config text
    """
    if proj_path.is_dir():
        print("%s already exists" % proj_path)
    else:
        proj_path.mkdir()
        print("Create %s" % proj_path)

    config_path = proj_path.joinpath("config")
    if config_path.is_dir():
        print("%s already exists" % config_path)
    else:
        config_path.mkdir()
        print("Create %s" % config_path)

    default_conf = config_path.joinpath("default.conf")
    if default_conf.is_file():
        print("%s already exists" % default_conf)
    else:
        template_config_string = template_config_callback()
        with open(str(default_conf), "w") as f:
            f.write(template_config_string)
        print("Create %s" % default_conf)

    log_path = proj_path.joinpath("log")
    if not log_path.is_dir():
        log_path.mkdir()
        print("Create %s" % log_path)

def generate_webadmin_auth(interactive=True):
    """
    Generate a user and password in ini-format.
    Prints result to stdout.
    Can be copy-pasted into ``config/default.conf``

    :param bool interactive: ask for user/pass if True. Generate automatically if not.

    """
    from .Engines import utils

    secret_key = utils.create_new_secret()

    if interactive:
        admin_user = input("new admin username: ")
        admin_pw = getpass.getpass("new admin password: ")
    else:
        admin_user = "admin"
        admin_pw = utils.create_new_secret()
        print("generated password: {}".format(admin_pw))
                    
    admin_pw_hash = utils.create_pass(admin_pw)
    print("[webadmin]")
    print("user = {}".format(admin_user))
    print("password_hash = {}".format(admin_pw_hash))
    print("secret_key = {}".format(secret_key))

def generate_certificate(interactive=True):
    """
    Generate ssl certificates using openssl.
    Files is created in project folder.

        - certificate.pem.key
        - certificate.pem
        - certificate.der.key
        - certificate.der

    Prints result to stdout.

    :param bool interactive: ask for CN if True.
    """

    from .Engines import utils

    if not utils.can_generate_certs():
        print("Operation failed. openssl not available in system path.")
        return

    pem_file = utils.default_pem_file
    key_file = utils.default_key_file
    der_file = utils.default_der_file
    derkey_file = utils.default_derkey_file
    common_name = ""

    if interactive:
        for fn in (pem_file, key_file, der_file, derkey_file):
            if pathlib.Path(fn).is_file():
                res = input("{} already exists. Overwrite? ([Y]/n) ".format(fn)).lower()
                if not (res == "" or res == "y"):
                    print("Operation aborted by user")
                    return
        cn = input("Common name: ")
        if cn:
            common_name = cn

    res = utils.generate_overwrite_certificates(pem_file, key_file, der_file, derkey_file, common_name)
    if res:
        print("Error")
        print(res)
    else:
        print("New certs generated successfully:")
        for fn in (pem_file, key_file, der_file, derkey_file):
            print(fn)

def framework_entrypoint():
    """
    The main entrypoint for the netdef package. Used by :func:`cli`.

    Parses command line arguments and dispatch functions

    """
    global_parser = ArgumentParser(add_help=True)
    global_parser.add_argument('-n', '--non-interactive', action='store_true', help='do not prompt for user/pass')
    global_parser.add_argument('-ga', '--generate-auth', action='store_true', help='generate webadmin authentication')
    global_parser.add_argument('-gc', '--generate-certificate', action='store_true', help='generate ssl certificate')

    args = global_parser.parse_args()

    if args.generate_auth:
        generate_webadmin_auth(interactive=not args.non_interactive)
    elif args.generate_certificate:
        generate_certificate(interactive=not args.non_interactive)
    else:
        global_parser.print_help()

def cli():
    """
    entrypoint for use in ``setup.py``::

        entry_points={
            'console_scripts': [
                '{NAME}={MAIN_PACKAGE}.__main__:cli'.format(NAME=NAME, MAIN_PACKAGE=MAIN_PACKAGE),
            ],
        },
    """
    # entrypoint: console_scripts
    # entrypoint(run_app, get_template_config)
    framework_entrypoint()

if __name__ == '__main__':
    # entrypoint: python -m console_scripts 
    # entrypoint(run_app, get_template_config)
    framework_entrypoint()

