import logging
import pathlib
from flask import Flask
import flask_admin
import flask_login
from werkzeug.serving import run_simple

#from werkzeug.security import generate_password_hash, check_password_hash

from . import ThreadedEngine
from .webadmin import AdminIndex, Views

log = logging.getLogger("ThreadedWebGuiEngine")
log.info("Enter Threaded Web Gui Engine")

class ThreadedWebGuiEngine(ThreadedEngine.ThreadedEngine):
    def __init__(self, shared):
        super().__init__(shared)
        self.webadmin_views = Views.Views(shared)
        self.app = None
    
    def load(self, base_package):
        super().load(base_package)
        self.webadmin_views.load(base_package)
    
    def init(self):
        super().init()
        self.app = init_app(self.webadmin_views, self.shared)

    def block(self):
        # main-funksjonen avslutter når denne funksjonen returnerer
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

        # her startes webserveren, denne blokkerer til ctrl-c mottas
        try:
            run_simple(host, port, self.app, use_reloader=False, use_debugger=False, threaded=True, ssl_context=ssl_context)
        except KeyboardInterrupt:
            pass

def init_app(webadmin_views, shared):
    """konfigurering av Flask.
    """
    config = shared.config.config
    section = "webadmin"

    shared.config.set_hidden_value(section, "user")
    shared.config.set_hidden_value(section, "password")
    shared.config.set_hidden_value(section, "password_hash")
    shared.config.set_hidden_value(section, "secret_key")

    template_path = shared.config.config("install", "path", "") + "/Engines/templates"

    # henter bruker/pass fra konfig
    admin_user = config(section, "user", "admin", add_if_not_exists=False)
    admin_password = config(section, "password", "", add_if_not_exists=False)
    admin_password_hash = config(section, "password_hash", "", add_if_not_exists=False)
    secret_key = "\x94\x03\x9c\x15\x00\xbf\x8c\xdd\xfef\xf8D]\xcc\xbf\xd4\xb6\xf3\x9a\xfe\x80\xa2\x90n"
    secret_key = config(section, "secret_key", secret_key, add_if_not_exists=False)

    app = Flask(__name__, template_folder='templates', static_folder='static')

    # dersom vi har overstyrt denne modulen og det finnes en annen template-mappe
    # så blir den fanget opp i variabelen template_path og lagt til i jinja sin
    # søkefilsti
    try:
        if not pathlib.Path(__file__).parent.joinpath("templates").samefile(template_path):
            template_search_path = app.jinja_loader.searchpath
            template_search_path.insert(0, template_path)
    except FileNotFoundError:
        pass

    # globale innstillinger og instanser legges til i app.config
    # andre moduler kan hente disse med "import current_app"
    app.config['ADMIN_USER'] = admin_user
    app.config['ADMIN_PASSWORD'] = admin_password
    app.config['ADMIN_PASSWORD_HASH'] = admin_password_hash
    app.config['SECRET_KEY'] = secret_key
    app.config['SHARED'] = shared
    #app.config['RSTPAGES_SRC'] = pathlib.Path('docs').absolute()

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(login):
        if login not in (admin_user):
            return
        user = AdminIndex.User()
        user.id = login
        return user

    @app.route('/')
    def index():
        return '<a href="/admin/">Webadmin</a>'

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
