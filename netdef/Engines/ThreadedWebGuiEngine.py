import logging
import pathlib
from flask import Flask, redirect
import flask_admin
import flask_login
from werkzeug.serving import run_simple

#from werkzeug.security import generate_password_hash, check_password_hash

from . import ThreadedEngine
from .webadmin import AdminIndex, Views

log = logging.getLogger("ThreadedWebGuiEngine")
log.info("Enter Threaded Web Gui Engine")

class ThreadedWebGuiEngine(ThreadedEngine.ThreadedEngine):
    """
    Integrates a simple werkzeug webserver to serve flask_admin webpages
    """
    def __init__(self, shared):
        super().__init__(shared)
        self.webadmin_views = Views.Views(shared)
        self.app = None
    
    def load(self, base_package):
        super().load(base_package)
        self.webadmin_views.load(base_package)
    
    def init(self):
        super().init()
        app = self.get_flask_app()
        init_app(app, self.webadmin_views, self.shared)

    def block(self):
        "Run webserver and wait for KeyboardInterrupt"

        log.info("run web interface")
        section = "webadmin"

        config = self.shared.config.config
        host = config(section, "host", "")
        port = config(section, "port", 8000)
        log.info("%s %s", host, port)

        ssl_certificate = config(section, "ssl_certificate", "")
        ssl_certificate_key = config(section, "ssl_certificate_key", "")
        ssl_on = config(section, "ssl_on", 0)

        ssl_context = None
        if ssl_on:
            if ssl_certificate and ssl_certificate_key:
                ssl_context = (ssl_certificate, ssl_certificate_key)

        # run webserver. blocks until ctrl-c is received
        try:
            run_simple(host, port, self.app, use_reloader=False, use_debugger=False, threaded=True, ssl_context=ssl_context)
        except KeyboardInterrupt:
            pass
    
    def get_flask_app(self):
        """
        Returns the main flask app.

        Common use case is to integrate an existing flask app.
        
        main.py Example::

            def init_app(app):

                @app.route('/')
                def hello_world():
                    return 'Hello, World!'
                
                return app


            def main():
                ...

                engine = ThreadedWebGuiEngine.ThreadedWebGuiEngine(shared)

                # here we go
                init_app(engine.get_flask_app())

                engine.add_controller_classes(controllers)
                engine.add_source_classes(sources)
                engine.add_rule_classes(rules)
                engine.load([__package__, 'netdef'])
                engine.init()
                engine.start()
                engine.block() # until ctrl-c or SIG_TERM
                engine.stop()
                ...

        """
        if not self.app:
            self.app = Flask(__name__, template_folder='templates', static_folder='static')
        return self.app

def init_app(app, webadmin_views, shared):
    """Configure flask. Setup flask_admin and flask_login
    """
    config = shared.config
    section = "webadmin"

    template_path = shared.config.config("install", "path", "") + "/Engines/templates"

    admin_users = make_admin_users_dict(config, section)

    config.set_hidden_value(section, "secret_key")
    secret_key = "\x94\x03\x9c\x15\x00\xbf\x8c\xdd\xfef\xf8D]\xcc\xbf\xd4\xb6\xf3\x9a\xfe\x80\xa2\x90n"
    secret_key = config(section, "secret_key", secret_key, add_if_not_exists=False)

    # if we have overridden this module and there is another template directory
    # then it is captured in the template_path variable and added to its jinja
    # search file path
    try:
        if not pathlib.Path(__file__).parent.joinpath("templates").samefile(template_path):
            template_search_path = app.jinja_loader.searchpath
            template_search_path.insert(0, template_path)
    except FileNotFoundError:
        pass

    # global settings and instances are added to app.config
    # other modules can retrieve these with "import current_app"
    app.config['ADMIN_USERS'] = admin_users
    app.config['SECRET_KEY'] = secret_key
    app.config['SHARED'] = shared
    #app.config['RSTPAGES_SRC'] = pathlib.Path('docs').absolute()

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(login):
        if login not in (admin_users.keys()):
            return
        user = AdminIndex.User(login, admin_users[login]["roles"])
        return user

    @app.route('/')
    def index():
        return redirect("/admin/", code=302)

    webadmin_on = config(section, "on", 1)
    if webadmin_on:
        # Create admin interface
        admin = flask_admin.Admin(
            name="Webadmin",
            index_view=AdminIndex.MyAdminIndexView(),
            template_mode='bootstrap3')

        admin.init_app(app)
        webadmin_views.setup(admin)

    return app


def make_admin_users_dict(config, section):
    # fetch legacy user/pass from konfig
    admin_user = config.config(section, "user", "admin", add_if_not_exists=False)
    admin_password = config.config(section, "password", "", add_if_not_exists=False)
    admin_password_hash = config.config(section, "password_hash", "", add_if_not_exists=False)

    # new rolebased user/pass
    admin_users = {}

    if admin_user:
        config.set_hidden_value(section, "user")
        config.set_hidden_value(section, "password")
        config.set_hidden_value(section, "password_hash")

        admin_users[admin_user] =  {
            "password": admin_password,
            "password_hash": admin_password_hash,
            "roles": {"admin"}
        }
    
    prefixes = {}

    for key, val in config.get_dict("webadmin").items():
        if key.startswith("users.") and key.count(".") == 2:
            prefix, attr = key.split(".")[1:3]
            if attr in ("user", "password", "password_hash", "roles"):
                if not prefix in prefixes:
                    prefixes[prefix] = {
                        "user":"", "password":"", "password_hash":"", "roles":set()
                    }
                if attr == "roles":
                    prefixes[prefix][attr] = set(map(str.strip, val.split(",")))
                else:
                    config.set_hidden_value(section, key)
                    prefixes[prefix][attr] = val

    for user_info in prefixes.values():
        admin_users[user_info["user"]] = user_info
    
    return admin_users
