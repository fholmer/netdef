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

    global_parser = ArgumentParser(add_help=True)
    global_parser.add_argument('proj_path', type=pathlib.Path, help='path to project directory')
    global_parser.add_argument('-i', '--init', action='store_true', help='setup project directory')
    global_parser.add_argument('-g', '--generate-auth', action='store_true', help='generate webadmin authentication')
    global_parser.add_argument('-r', '--run', action='store_true', help='start application')
    args = global_parser.parse_args()

    proj_path = args.proj_path.expanduser().absolute()
    os.chdir(str(proj_path))

    if args.init:
        create_project(proj_path, template_config_callback)
    elif args.generate_auth:
        generate_webadmin_auth()
    elif args.run:
        run_callback()
    else:
        print("Proj path: {}".format(proj_path))
        print("use argument -r, --run to start application")

def create_project(proj_path, template_config_callback):
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

def generate_webadmin_auth(interative=True):
    import werkzeug.security
    import binascii

    secret_key = binascii.hexlify(os.urandom(16)).decode('ascii')

    if interative:
        admin_user = input("new admin username: ")
        admin_pw = getpass.getpass("new admin password: ")
    else:
        admin_user = "admin"
        admin_pw = binascii.hexlify(os.urandom(8)).decode('ascii')
        print("generated password: {}".format(admin_pw))

    admin_pw_hash = werkzeug.security.generate_password_hash(admin_pw).replace("$", "$$")
    print("[webadmin]")
    print("user = {}".format(admin_user))
    print("password_hash = {}".format(admin_pw_hash))
    print("secret_key = {}".format(secret_key))

def framework_entrypoint():
    global_parser = ArgumentParser(add_help=True)
    global_parser.add_argument('-n', '--non-interactive', action='store_true', help='do not prompt for user/pass')
    global_parser.add_argument('-g', '--generate-auth', action='store_true', help='generate webadmin authentication')
    args = global_parser.parse_args()

    if args.generate_auth:
        generate_webadmin_auth(interative=not args.non_interactive)
    else:
        global_parser.print_help()

def cli():
    # entrypoint: console_scripts
    # entrypoint(run_app, get_template_config)
    framework_entrypoint()

if __name__ == '__main__':
    # entrypoint: python -m console_scripts 
    # entrypoint(run_app, get_template_config)
    framework_entrypoint()

