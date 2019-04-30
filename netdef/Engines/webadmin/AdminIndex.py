from flask import url_for, redirect, request, current_app
from wtforms import form, fields, validators
import werkzeug.security
import flask_admin
from flask_admin import helpers, expose
import flask_login
from ... import __version__ as version

def shutdown_server():
    func = current_app.config.get("server.shutdown")
    if func is None:
        func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Cannot shutdown. Not running with the Werkzeug Server')
    func()

class MyAdminIndexView(flask_admin.AdminIndexView):
    restarting = 0
    shuttingdown = 0

    @expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return self.render(self._template, version=version)

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            flask_login.login_user(user)

        if flask_login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        flask_login.logout_user()
        return redirect(url_for('.index'))

    @expose('/restart/')
    def restart_view(self):
        shared = current_app.config["SHARED"]
        shared.restart_on_exit = True
        self.restarting = 1
        shutdown_server()
        return redirect(url_for('.command_result_view'))

    @expose('/command_result/')
    def command_result_view(self):
        if self.restarting > 0:
            return "Restarting ..."
        elif self.shuttingdown > 0:
            return "Shutting down ..."
        else:
            return redirect(url_for('.index'))
            
    @expose('/shutdown/')
    def shutdown_view(self):
        shared = current_app.config["SHARED"]
        shared.restart_on_exit = False
        self.shuttingdown = 1
        shutdown_server()
        return redirect(url_for('.command_result_view'))
    
class User(flask_login.UserMixin):
    pass

class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('Invalid user')
        
        # sjekker om pwhash er benyttet
        admin_pw_hash = current_app.config["ADMIN_PASSWORD_HASH"]
        admin_pw_hash = admin_pw_hash.replace("$$", "$")

        if admin_pw_hash:
             if not werkzeug.security.check_password_hash(admin_pw_hash, self.password.data):
                raise validators.ValidationError('Invalid password')
        else:
            # fallback til plaintext
            admin_password = current_app.config["ADMIN_PASSWORD"]
            if self.password.data != admin_password:
                raise validators.ValidationError('Invalid password')

    def get_user(self):
        admin_user = current_app.config["ADMIN_USER"]
        if self.login.data == admin_user:
            user = User()
            user.id = self.login.data
            return user
        return None
