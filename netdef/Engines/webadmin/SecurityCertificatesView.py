import configparser
import functools
import glob
from wtforms import Form, StringField, PasswordField, validators, SelectField
from flask import current_app, request, flash
from flask_admin import expose
from .MyBaseView import MyBaseView
from . import Views
from .. import utils

@Views.register("SecurityCertificatesView")
def setup(admin, view=None):
    config = admin.app.config['SHARED'].config.config
    security_certificates_on = config("webadmin", "security_certificates_on", 1)

    if security_certificates_on:
        admin.app.config["tools_panels"]["security_panel_on"] = 1
        admin.app.config["tools_panels"]["security_certificates_on"] = 1

        if not view:
            view = SecurityCertificatesView(name='Certificates', endpoint='security_certificates')
        admin.app.register_blueprint(view.create_blueprint(admin))

_pem_cert = utils.default_pem_file
_pem_key = utils.default_key_file
_der_cert = utils.default_der_file
_der_key = utils.default_derkey_file

class SecurityCertificatesForm(Form):
    current_password = PasswordField('Current password')

    @staticmethod
    def validate_current_password(form, field):
        validators.DataRequired()(form, field)
        if not utils.check_user_and_pass(current_app, field.data):
            raise validators.ValidationError('Invalid password')

    cn = StringField('Common name', validators=[validators.Regexp("^[a-zA-Z0-9._-]*$", message="valid chars: a-z, A-Z, 0-9, ._-")])
    pem_cert = SelectField('PEM cert', default=_pem_cert, choices=[(_pem_cert, _pem_cert)])
    pem_key =  SelectField('PEM key',  default=_pem_key, choices=[(_pem_key, _pem_key)])
    der_cert = SelectField('DER cert', default=_der_cert, choices=[(_der_cert, _der_cert)])
    der_key =  SelectField('DER key', default=_der_key, choices=[(_der_key, _der_key)])

class SecurityCertificatesView(MyBaseView):
    @expose("/", methods=['GET', 'POST'])
    def index(self):
        conf_ok = utils.can_generate_certs()
        form = SecurityCertificatesForm(request.form)

        if request.method == 'POST' and form.validate():
            flash("Generating certs...", category="info")
            
            utils.generate_overwrite_certificates(
                _pem_cert,
                _pem_key,
                _der_cert,
                _der_key,
                form.cn.data
            )

            flash("New certs generated successfully", category="success")

        return self.render(
            'security/certificates.html',
            conf_ok=conf_ok,
            form=form
        )
