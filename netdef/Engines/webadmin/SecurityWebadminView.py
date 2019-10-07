import configparser
import functools
import glob
from wtforms import Form, StringField, PasswordField, validators, BooleanField, SelectField
from flask import current_app, request, flash
from flask_admin import expose
from .AdminIndex import check_user_and_pass, create_pass, create_new_secret
from .MyBaseView import MyBaseView
from . import Views

@Views.register("SecurityWebadminView")
def setup(admin, view=None):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_security_on = config(section, "security_webadmin_on", 0)

    if webadmin_security_on:
        admin.app.config["tools_panels"]["webadmin_security_on"] = 1
        admin.app.config["tools_panels"]["security_panel_on"] = 1
        if not view:
            view = SecurityWebadminView(name='Security Webadmin', endpoint='security_webadmin')
        admin.app.register_blueprint(view.create_blueprint(admin))
        # admin.add_view(view)

webadmin_conf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
webadmin_conf.optionxform = str
webadmin_conf.add_section("webadmin")

default = {
    "user": functools.partial(webadmin_conf.get, "webadmin", "user", fallback="admin"),
    "ssl_on": functools.partial(webadmin_conf.get, "webadmin", "ssl_on", fallback="0"),
    "ssl_certificate": functools.partial(webadmin_conf.get, "webadmin", "ssl_certificate", fallback=""),
    "ssl_certificate_key": functools.partial(webadmin_conf.get, "webadmin", "ssl_certificate_key", fallback="")
}

class SecurityForm(Form):
    choices_crts = [("", "None")] + [(c,c) for c in glob.glob("**/*.pem", recursive=True)]
    choices_keys = [("", "None")] + [(c,c) for c in glob.glob("**/*.key", recursive=True)]

    login = StringField('Login', [validators.Required()], default=default["user"])
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
    new_flask_secret = BooleanField("Renew session cookie")
    ssl_on = SelectField("HTTPS On", default=default["ssl_on"], choices=[("0", "Off"), ("1", "On")])
    ssl_certificate = SelectField('SSL Certificate', default=default["ssl_certificate"], choices=choices_crts)
    ssl_certificate_key = SelectField('SSL Key', default=default["ssl_certificate_key"], choices=choices_keys)


class SecurityWebadminView(MyBaseView):
    @expose("/", methods=['GET', 'POST'])
    def index(self):
        config = current_app.config["SHARED"].config
        conf_file = config("config", "webadmin_conf", "", add_if_not_exists=False)
        conf_ok = conf_file.startswith("config")
        webadmin_conf.read(conf_file, encoding=config.conf_encoding)

        form = SecurityForm(request.form)

        for key in form.ssl_certificate.choices:
            if key[0] == form.ssl_certificate.data:
                break
        else:
            form.ssl_certificate.choices.append((form.ssl_certificate.data, form.ssl_certificate.data))

        for key in form.ssl_certificate_key.choices:
            if key[0] == form.ssl_certificate_key.data:
                break
        else:
            form.ssl_certificate_key.choices.append((form.ssl_certificate_key.data, form.ssl_certificate_key.data))

        if request.method == 'POST' and form.validate():
            if form.old_password.data:
                if check_user_and_pass(current_app, form.old_password.data):
                    password = create_pass(form.password.data)
                    webadmin_conf.set("webadmin", "user", form.login.data)
                    webadmin_conf.set("webadmin", "password", "")
                    webadmin_conf.set("webadmin", "password_hash", password)
                    flash('Password has been changed.')
                else:
                    flash('Current password is invalid.')

            if form.new_flask_secret.data:
                secret = create_new_secret()
                webadmin_conf.set("webadmin", "secret_key", secret)

            webadmin_conf.set("webadmin", "ssl_on", form.ssl_on.data)
            webadmin_conf.set("webadmin", "ssl_certificate", form.ssl_certificate.data)
            webadmin_conf.set("webadmin", "ssl_certificate_key", form.ssl_certificate_key.data)
            webadmin_conf.write(open(conf_file, 'w'))

            flash("Changes to '{}' saved successfully.".format(conf_file), category="success")

        return self.render(
            'security/webadmin.html',
            conf_file=conf_file,
            conf_ok=conf_ok,
            form=form
        )
