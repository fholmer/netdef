import sys
import datetime
import subprocess
import platform
import pathlib
import psutil
from flask import current_app, stream_with_context, Response
from flask_admin import expose
from .MyBaseView import MyBaseView
from . import Views

APP_STARTUP = datetime.datetime.utcnow()
SYS_STARTUP = datetime.datetime.utcfromtimestamp(psutil.boot_time())

def stdout_from_terminal(*command, err_msg=None):
    try:
        res = subprocess.run(command, stdout=subprocess.PIPE).stdout
        return "<pre>" + str(res, errors="replace") + "</pre>"
    except Exception as error:
        if err_msg:
            return err_msg
        else:
            return str(error)

def stdout_from_terminal_as_generator(*command, err_msg=None, pre="", post=""):
    try:
        yield "<pre>"
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        if pre:
            yield pre
        for line in iter(process.stdout.readline, b''):
            yield str(line, errors="replace")
        if post:
            yield post
        yield "</pre>"
    except Exception as error:
        if err_msg:
            yield err_msg
        else:
            yield str(error)

def verify_update(cmd):
    if not len(cmd) > 4:
        return False
    elif not cmd[0].endswith("python"):
        return False
    elif cmd[1] != '-m':
        return False
    elif cmd[2] != 'pip':
        return False
    return True

def get_update_cmd(
            executable,
            no_index,
            pre,
            force_reinstall,
            find_links,
            trusted_host,
            minimal_timeout,
            package
        ):
    args = [executable, "-m", "pip", "install", "--upgrade", "-f"]
    args.append(str(pathlib.Path("./installation_repo").absolute()))

    if no_index:
        args.append("--no-index")
    if pre:
        args.append("--pre")
    if force_reinstall:
        args.append("--force-reinstall")
    if trusted_host:
        args.append("--trusted-host")
        args.append(trusted_host)
    if find_links:
        args.append("-f")
        args.append(find_links)
    if minimal_timeout:
        args.append("--retries 1")
        args.append("--timeout 1")
    args.append(package)
    return args


@Views.register("Tools")
def setup(admin, view=None):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_tools_on = config(section, "tools_on", 1)
    if webadmin_tools_on:
        if not view:
            view = Tools(name='Tools', endpoint='tools')
        admin.add_view(view)


class Tools(MyBaseView):
    @expose("/")
    def index(self):
        now = datetime.datetime.utcnow()
        app_diff = now - APP_STARTUP
        sys_diff = now - SYS_STARTUP
        return self.render(
            'tools.html',
            app_uptime=str(app_diff),
            sys_uptime=str(sys_diff),
            sys_version=str(platform.version())
        )

    @expose("/autoupgrade/")
    def autoupgrade(self):
        shared = current_app.config['SHARED']
        manage_repo = current_app.config['MANAGE_REPO']
        config = shared.config.config
        self.auto_update_on = config("auto_update", "on", 0)
        default_package_name = config("general", "identifier", "")
        self.auto_update_args = (
                config("auto_update", "no_index", 1),
                config("auto_update", "pre_release", 0),
                config("auto_update", "force_reinstall", 0),
                config("auto_update", "find_links", ""),
                config("auto_update", "trusted_host", ""),
                config("auto_update", "minimal_timeout", 0),
                config("auto_update", "package", default_package_name)
        )
        auto_update_args_names = (
            "no_index", "pre_release", "force_reinstall", "find_links",
            "trusted_host", "minimal_timeout", "package"
        )
        return self.render(
            'autoupgrade.html',
            auto_update_on=self.auto_update_on,
            manage_repo=manage_repo,
            update_args=zip(auto_update_args_names, self.auto_update_args)
        )
    
    @expose("/echo/")
    def echo(self):
        return stdout_from_terminal("echo", "test æøå €éê")

    @expose("/logfile/")
    def logfile(self):
        try:
            return "<pre>" + open("log/application.log").read() + "</pre>"
        except Exception as error:
            return str(error)

    @expose("/autoupgrade/upgrade/")
    def autoupgrade_upgrade(self):
        shared = current_app.config['SHARED']
        config = shared.config.config

        if not self.auto_update_on:
            return "ERROR: Update aborted. Update disabled i config"

        auto_update_cmd = get_update_cmd(
                sys.executable,
                *self.auto_update_args
            )

        if not verify_update(auto_update_cmd):
            return "ERROR: Update aborted. update command is rejected"
        
        return Response(
            stream_with_context(
                stdout_from_terminal_as_generator(*auto_update_cmd)
            )
        )
