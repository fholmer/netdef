import configparser
import functools
import glob
from wtforms import Form, StringField, SelectField
from flask import current_app, request, flash
from flask_admin import expose
from .MyBaseView import MyBaseView
from . import Views

@Views.register("SecurityBuiltinControllersView")
def setup(admin, view=None):
    config = admin.app.config['SHARED'].config.config
    security_builtin_controllers_on = config("webadmin", "security_builtin_controllers_on", 1)

    if security_builtin_controllers_on:
        admin.app.config["tools_panels"]["security_panel_on"] = 1
        admin.app.config["tools_panels"]["security_builtin_controllers_on"] = 1

        if not view:
            view = SecurityBuiltinControllersView(name='Security', endpoint='security_builtin_controllers')
        admin.app.register_blueprint(view.create_blueprint(admin))
        # admin.add_view(view)

security_conf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
#This trick allows the option key to remain case-sensitive
security_conf.optionxform = str
_config = None

def _getdef(section, key, val):
    fallback = _config(section, key, val)
    return security_conf.get(section, key, fallback=fallback)

def getdef(key, val):
    func = functools.partial(_getdef, "OPCUAServerController", key, val)
    return func

class OPCUAServerControllerForm(Form):
    choices_crts = [("", "None")] + [(c,c) for c in glob.glob("ssl/certs/*", recursive=True)]
    choices_keys = [("", "None")] + [(c,c) for c in glob.glob("ssl/private/*", recursive=True)]
    choices_on = [("0", "Off"), ("1", "On")]

    user = StringField('User', default=getdef("user", "user"))
    password = StringField('Password', default=getdef("password", "password"))
    endpoint = StringField('Endpoint', default=getdef("endpoint",  "no_endpoint"))
    certificate = SelectField('Certificate', default=getdef("certificate", ""), choices=choices_crts)
    private_key = SelectField('Private key', default=getdef("private_key", ""), choices=choices_keys)
    anonymous_on = SelectField('Anonymous access', default=getdef("anonymous_on", 0), choices=choices_on)
    username_on = SelectField('Username access', default=getdef("username_on", 1), choices=choices_on)
    nosecurity_on = SelectField('Security: None', default=getdef("nosecurity_on", 1), choices=choices_on)
    basic128rsa15_sign_on = \
        SelectField('Security: Basic128rsa15 Sign', default=getdef("basic128rsa15_sign_on", 0), choices=choices_on)
    basic128rsa15_signandencrypt_on = \
        SelectField('Security: Basic128rsa15 Sign&Encrypt', default=getdef("basic128rsa15_signandencrypt_on", 0), choices=choices_on)
    basic256_sign_on = \
        SelectField('Security: Basic256 Sign', default=getdef("basic256_sign_on", 0), choices=choices_on)
    basic256_signandencrypt_on = \
        SelectField('Security: Basic256 Sign&Encrypt', default=getdef("basic256_signandencrypt_on", 0), choices=choices_on)
    basic256sha256_sign_on = \
        SelectField('Security: Basic256sha256 Sign', default=getdef("basic256sha256_sign_on", 1), choices=choices_on)
    basic256sha256_signandencrypt_on = \
        SelectField('Security: Basic256sha256 Sign&Encrypt', default=getdef("basic256sha256_signandencrypt_on", 1), choices=choices_on)

class SecurityBuiltinControllersView(MyBaseView):
    @expose("/", methods=['GET', 'POST'])
    def index(self):
        global _config
        config = current_app.config["SHARED"].config
        _config = config.config

        conf_file = config("SecurityBuiltinControllersView", "conf_file", "")
        conf_ok = conf_file.startswith("config")

        security_conf.read(conf_file, encoding=config.conf_encoding)

        form = OPCUAServerControllerForm(request.form)

        for key in form.certificate.choices:
            if key[0] == form.certificate.data:
                break
        else:
            form.certificate.choices.append((form.certificate.data, form.certificate.data))

        for key in form.private_key.choices:
            if key[0] == form.private_key.data:
                break
        else:
            form.private_key.choices.append((form.private_key.data, form.private_key.data))

        section = "OPCUAServerController"
        if request.method == 'POST' and form.validate():
            security_conf.set(section, "user", form.user.data)
            security_conf.set(section, "password", form.password.data)
            security_conf.set(section, "password_hash", "")
            security_conf.set(section, "endpoint", form.endpoint.data)
            security_conf.set(section, "certificate", form.certificate.data)
            security_conf.set(section, "private_key", form.private_key.data)
            security_conf.set(section, "anonymous_on", form.anonymous_on.data)
            security_conf.set(section, "username_on", form.username_on.data)
            security_conf.set(section, "nosecurity_on", form.nosecurity_on.data)
            security_conf.set(section, "basic128rsa15_sign_on", form.basic128rsa15_sign_on.data)
            security_conf.set(section, "basic128rsa15_signandencrypt_on", form.basic128rsa15_signandencrypt_on.data)
            security_conf.set(section, "basic256_sign_on", form.basic256_sign_on.data)
            security_conf.set(section, "basic256_signandencrypt_on", form.basic256_signandencrypt_on.data)
            security_conf.set(section, "basic256sha256_sign_on", form.basic256sha256_sign_on.data)
            security_conf.set(section, "basic256sha256_signandencrypt_on", form.basic256sha256_signandencrypt_on.data)

            security_conf.write(open(conf_file, 'w'))
            flash("Changes to '{}' saved successfully.".format(conf_file), category="success")

        return self.render(
            'security/builtin_controllers.html',
            conf_file=conf_file,
            conf_ok=conf_ok,
            form=form
        )
