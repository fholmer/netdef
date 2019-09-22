import sys
import datetime
import subprocess
import platform
import pathlib
import configparser
import functools
from wtforms import Form, StringField, PasswordField, validators, BooleanField
from flask import current_app, url_for, redirect, request, flash, stream_with_context, Response
from flask_admin import expose
from .AdminIndex import check_user_and_pass, create_pass, create_new_secret
from .MyBaseView import MyBaseView
from . import Views

@Views.register("SecuritySettingsView")
def setup(admin, view=None):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_tools_on = config(section, "security_settings_on", 0)

    if webadmin_tools_on:
        if not view:
            view = SecuritySettingsView(name='Security', endpoint='SecuritySettings')
        admin.add_view(view)


security_conf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
security_conf.add_section("webadmin")
login_name = functools.partial(security_conf.get, "webadmin", "user", fallback="admin")

class RegistrationForm(Form):
    login = StringField('Login', [validators.Required()], default=login_name)
    old_password = PasswordField('Current password', validators=[validators.required()])

    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    new_flask_secret = BooleanField("Renew secret key")

class SecuritySettingsView(MyBaseView):
    @expose("/", methods=['GET', 'POST'])
    def index(self):
        config = current_app.config["SHARED"].config
        conf_file = config("config", "security_conf", "", add_if_not_exists=False)
        conf_ok = conf_file.startswith("config")

        security_conf.read(conf_file, encoding=config.conf_encoding)

        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            if check_user_and_pass(current_app, form.old_password.data):

                if form.new_flask_secret.data:
                    secret = create_new_secret()
                    security_conf.set("webadmin", "secret_key", secret)

                password = create_pass(form.password.data)

                security_conf.set("webadmin", "user", form.login.data)
                security_conf.set("webadmin", "password", "")
                security_conf.set("webadmin", "password_hash", password)
                
                security_conf.write(open(conf_file, 'w'))
                flash('Password has been changed.')
            else:
                flash('Current password is invalid.')

        return self.render(
            'security_settings.html',
            conf_file=conf_file,
            conf_ok=conf_ok,
            form=form
        )
