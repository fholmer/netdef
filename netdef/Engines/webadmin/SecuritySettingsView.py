import sys
import datetime
import subprocess
import platform
import pathlib
import configparser
import functools
import glob
from wtforms import Form, StringField, PasswordField, validators, BooleanField, SelectField
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
ssl_on = functools.partial(security_conf.get, "webadmin", "ssl_on", fallback="0")
ssl_certificate = functools.partial(security_conf.get, "webadmin", "ssl_certificate", fallback="")
ssl_certificate_key = functools.partial(security_conf.get, "webadmin", "ssl_certificate_key", fallback="")

crt_choices = [("", "None")] + [(c,c) for c in glob.glob("**/*.pem", recursive=True)]
key_choices = [("", "None")] + [(c,c) for c in glob.glob("**/*.key", recursive=True)]

class SecurityForm(Form):
    login = StringField('Login', [validators.Required()], default=login_name)

    old_password = PasswordField('Current password')

    @staticmethod
    def validate_old_password(form, field):
        if form["password"].data:
            validators.DataRequired()(form, field)
            if not check_user_and_pass(current_app, field.data):
                raise validators.ValidationError('Invalid password')

    password = PasswordField('New Password')

    @staticmethod
    def validate_password(form, field):
        if form["old_password"].data:
            validators.DataRequired()(form, field)
            validators.EqualTo('confirm', message='Passwords must match')(form, field)

    confirm = PasswordField('Repeat Password')
    new_flask_secret = BooleanField("Renew secret key")
    ssl_on = SelectField("HTTPS On", default=ssl_on, choices=[("0", "Off"), ("1", "On")])
    ssl_certificate = SelectField('SSL Certificate', default=ssl_certificate, choices=crt_choices)
    ssl_certificate_key = SelectField('SSL Key', default=ssl_certificate_key, choices=key_choices)


class SecuritySettingsView(MyBaseView):
    @expose("/", methods=['GET', 'POST'])
    def index(self):
        config = current_app.config["SHARED"].config
        conf_file = config("config", "security_conf", "", add_if_not_exists=False)
        conf_ok = conf_file.startswith("config")

        security_conf.read(conf_file, encoding=config.conf_encoding)

        form = SecurityForm(request.form)
        if request.method == 'POST' and form.validate():
            if form.old_password.data:
                if check_user_and_pass(current_app, form.old_password.data):
                    password = create_pass(form.password.data)
                    security_conf.set("webadmin", "user", form.login.data)
                    security_conf.set("webadmin", "password", "")
                    security_conf.set("webadmin", "password_hash", password)
                    flash('Password has been changed.')
                else:
                    flash('Current password is invalid.')

            if form.new_flask_secret.data:
                secret = create_new_secret()
                security_conf.set("webadmin", "secret_key", secret)

            security_conf.set("webadmin", "ssl_on", form.ssl_on.data)
            security_conf.set("webadmin", "ssl_certificate", form.ssl_certificate.data)
            security_conf.set("webadmin", "ssl_certificate_key", form.ssl_certificate_key.data)
            security_conf.write(open(conf_file, 'w'))

            flash("'{}' is updated.".format(conf_file))

        return self.render(
            'security_settings.html',
            conf_file=conf_file,
            conf_ok=conf_ok,
            form=form
        )
