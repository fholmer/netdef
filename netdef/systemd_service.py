"""
``netdef.systemd_service`` can also be invoked directly using the -m switch of
the interpreter with proj_path as argument.
    
This example installs the project in current directory as a service:

.. code-block:: console

    $ python -m netdef.systemd_service -i .

"""

import pathlib
import os
import sys
import shutil
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import namedtuple

ApplicationService = namedtuple('ApplicationService', ['svc_name', 'exe_name', 'app_callback', 'template_callback'])

SYSTEMD_UNIT_TEMPLATE = """[Unit]
Description={DESC}
After=syslog.target network-online.target

[Service]
Type=simple
User={USER}
Group={USER}
Environment=PYTHONUNBUFFERED=true

WorkingDirectory={WD}
ExecStart={EXEC} -r {WD}

StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target

"""

def get_service(svc_name, exe_name, app_callback, template_callback):
    """
    .. note::
        This function is only implemented for Windows and Systemd based linux
        distributions
    
    Returns the Service-class to use as argument in :func:`run_service`

    :param svc_name: name of the service
    :param exe_name: filename of the service
    :param app_callback: a function that will start your application
    :param template_callback: a function that returns template config
    :return: :class:`GenericApplicationService`

    Example:

    .. code-block:: python

        from netdef.service import get_service, run_service

        def run_app():
            from . import main

        def get_template_config():
            from . import defaultconfig
            return defaultconfig.template_config_string

        application_service = get_service("First-App", "First-App-Service", run_app, get_template_config)
        run_service(application_service)
    """

    # template_callback: not to be confused with SYSTEMD_UNIT_TEMPLATE
    # we will not be using template_callback in this systemd service
    #

    if not pathlib.Path(exe_name).suffix:
        exe_name = str(pathlib.Path(exe_name).with_suffix('.service')).lower()

    app_service = ApplicationService(
        svc_name=svc_name,
        exe_name=exe_name,
        app_callback=app_callback,
        template_callback=template_callback
    )
    return app_service

def run_service(app_service_class):
    """
    .. note::
        This function is only implemented for Windows and Systemd based linux
        distributions

    :param app_service_class: service class from :func:`get_service`

    Create an instance of `app_service_class` and run as service

    Example:

    .. code-block:: python

        from netdef.service import get_service, run_service

        def run_app():
            from . import main

        def get_template_config():
            from . import defaultconfig
            return defaultconfig.template_config_string

        application_service = get_service("First-App", "First-App-Service", run_app, get_template_config)
        run_service(application_service)
    """

    cmd_parser = ArgumentParser(add_help=True)
    cmd_parser.add_argument('proj_path', type=pathlib.Path, help='path to project directory')
    cmd_parser.add_argument('-i', '--install', action='store_true', help='install as systemd service')
    cmd_parser.add_argument('-u', '--user', action='store', help='install as given user', default=os.getlogin())
    args = cmd_parser.parse_args()

    service_file = pathlib.Path("/etc/systemd/system").joinpath(app_service_class.exe_name)
    proj_path = args.proj_path.expanduser().absolute()
    os.chdir(str(proj_path))

    if args.install:
        install_service(proj_path, service_file, app_service_class.svc_name, args.user)
    else:
        cmd_parser.print_usage()
        print("Proj path: {}".format(proj_path))

def install_service(proj_path, service_file, svc_name, user):
    """
    .. note::
        This function is only implemented for Systemd based linux
        distributions

    Creates a systemd service file in /etc/systemd/system/

    """

    # check available applications

    if shutil.which("systemctl") is None:
        print("Operation failed. systemctl not available in system path.")
        return

    # check folder access
    if not os.access(str(service_file.parent), os.W_OK):
        print("Operation failed. Cannot write to {}/".format(service_file.parent))
        print("Try again using sudo or login as root.")

        if sys.argv[0] == __file__:
            # when "python -m netdef.systemd_service"
            args = [sys.executable, '-m', 'netdef.systemd_service'] + sys.argv[1:]
        else:
            args = sys.argv

        print("TIP: Use full path to executable:  $", " ".join(["sudo"] + args))
        return

    exec_dir = pathlib.Path(sys.executable).parent
    exec_file = exec_dir.joinpath(svc_name)

    # check file requirements

    if not exec_file.is_file():
        print("Operation failed. File not found:\n    {}".format(exec_file))
        return

    if service_file.is_file():
        res = input("""WARNING:
    File already exists and will be overwritten:
        {}
    
    Continue? (y/[N]): """.format(service_file))

        if res.lower() == "y":
            print("")
        else:
            print("Operation aborted by user")
            return

    message = """Systemd service will be created with parameters:

             filename: {FN}
          description: {DESC}
                 user: {USER}
                group: {USER}
    working directory: {WD}
      executable-path: {EXEC}
 executable-arguments: -r {WD}

 Continue? (y/[N]): """

    res = input(message.format(
        FN=service_file,
        DESC=svc_name,
        WD=proj_path,
        USER=user,
        EXEC=exec_file
    ))
    if not res.lower() == "y":
        print("Operation aborted by user")
        return

    service_file.write_text(
        SYSTEMD_UNIT_TEMPLATE.format(
            DESC=svc_name,
            WD=proj_path,
            USER=user,
            EXEC=exec_file
        )
    )

    service_name = service_file.name

    print("")
    print("Service is now ready")

    print("Reload systemd:     ", "$ systemctl --system daemon-reload")
    print("Enable the service: ", "$ systemctl enable " + service_name)
    print("Start the service:  ", "$ systemctl start " + service_name)

if __name__ == '__main__':
    default_name = str(pathlib.Path(".").expanduser().absolute().name)

    cmd_parser = ArgumentParser(add_help=True, formatter_class=ArgumentDefaultsHelpFormatter)
    cmd_parser.add_argument('proj_path', type=pathlib.Path, help='path to project directory')
    cmd_parser.add_argument('-i', '--install', action='store_true', help='install as systemd service')
    cmd_parser.add_argument('-u', '--user', action='store', help='install as given user', default=os.getlogin())
    cmd_parser.add_argument('-n', '--name', action='store', help='application name', default=default_name)
    args = cmd_parser.parse_args()

    app_service_class = get_service(args.name, args.name, None, None)

    service_file = pathlib.Path("/etc/systemd/system").joinpath(app_service_class.exe_name)
    proj_path = args.proj_path.expanduser().absolute()
    os.chdir(str(proj_path))

    if args.install:
        install_service(proj_path, service_file, app_service_class.svc_name, args.user)
    else:
        cmd_parser.print_usage()
        print("Proj path: {}".format(proj_path))
        print("use argument -i, --install to install as service")
