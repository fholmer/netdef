import configparser
import functools
import glob

import flask_login
from flask import current_app, flash, request
from flask_admin import expose
from flask_admin.form import FormOpts, rules
from wtforms import (
    Form,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    validators,
)

from .. import utils
from . import Views
from .MyBaseView import MyBaseView

_ip_addresses = list(utils.get_ip_addresses()) + ["", "", "", "", ""]
_shared_config = None


def get_uri():
    if _shared_config:
        return _shared_config("OPCUAServerController", "uri", _opcua_urn)
    else:
        return _opcua_urn


default = {
    "cn": utils.get_host_names()[0],
    "urn.1": get_uri,
    "dns.1": utils.get_host_names()[0],
    "ip.1": _ip_addresses[0],
    "ip.2": _ip_addresses[1],
    "ip.3": _ip_addresses[2],
    "ip.4": _ip_addresses[3],
    "ip.5": _ip_addresses[4],
    "basicConstraints": "CA:TRUE",
    "keyUsage": "critical, cRLSign, digitalSignature, keyCertSign",
    "extendedKeyUsage": "critical, serverAuth",
}


@Views.register("SecurityCertificatesView")
def setup(admin, view=None):
    config = admin.app.config["SHARED"].config.config
    global _shared_config
    _shared_config = config

    security_certificates_on = config("webadmin", "security_certificates_on", 1)

    if security_certificates_on:
        admin.app.config["tools_panels"]["security_panel_on"] = 1
        admin.app.config["tools_panels"]["security_certificates_on"] = 1

        if not view:
            view = SecurityCertificatesView(
                name="Certificates", endpoint="security_certificates"
            )
        admin.app.register_blueprint(view.create_blueprint(admin))


_webadmin_pem_cert = utils.default_webadmin_pem_file
_webadmin_pem_key = utils.default_webadmin_key_file
_webadmin_der_cert = utils.default_webadmin_der_file
_webadmin_der_key = utils.default_webadmin_derkey_file

_opcua_pem_cert = utils.default_opcua_pem_file
_opcua_pem_key = utils.default_opcua_key_file
_opcua_der_cert = utils.default_opcua_der_file
_opcua_der_key = utils.default_opcua_derkey_file
_opcua_urn = utils.default_opcua_urn

_form_rules = (
    rules.Header("Certificates"),
    rules.Field("gen_webadmin"),
    rules.Field("gen_opcua"),
    rules.Header("Common options"),
    rules.Field("cn"),
    rules.Field("days"),
    rules.Header("OpcUa options"),
    rules.Field("basicConstraints"),
    rules.Field("keyUsage"),
    rules.Field("extendedKeyUsage"),
    rules.Field("subjectAltName"),
    rules.Field("uri_1"),
    rules.Field("uri_2"),
    rules.Field("uri_3"),
    rules.Field("dns_1"),
    rules.Field("dns_2"),
    rules.Field("dns_3"),
    rules.Field("ip_1"),
    rules.Field("ip_2"),
    rules.Field("ip_3"),
    rules.Field("ip_4"),
    rules.Field("ip_5"),
    rules.Header("Confirmation"),
    rules.Field("current_password"),
    rules.Text("Confirm changes by entering webadmin password"),
)
_widget_args = {
    "current_password": {"column_class": "col-md-2"}
    # "gen_webadmin": {"column_class": "col-md-4"},
    # "gen_opcua": {"column_class": "col-md-4"}
}

_validate_dns = [
    validators.Regexp("^[a-zA-Z0-9._-]*$", message="valid chars: a-z, A-Z, 0-9, ._-")
]
_validate_url = [
    validators.Regexp(
        r"^[a-zA-Z0-9._\-:/]*$", message="valid chars: a-z, A-Z, 0-9, ._-:/"
    )
]
_validate_cmd = [
    validators.Regexp("^[a-zA-Z0-9, :]*$", message="valid chars: a-z, A-Z, 0-9, ,:")
]
_validate_ip = [validators.Optional(), validators.IPAddress()]


class SecurityCertificatesForm(Form):
    form_opts = FormOpts(widget_args=_widget_args, form_rules=_form_rules)
    gen_webadmin = SelectField(
        "Webadmin certificate",
        default="1",
        choices=[("0", "No change"), ("1", "Generate new")],
        description="Following files will be overwritten:<ul><li>{}</li><li>{}</li><li>{}</li><li>{}</li></ul>".format(
            _webadmin_pem_cert, _webadmin_pem_key, _webadmin_der_cert, _webadmin_der_key
        ),
    )
    gen_opcua = SelectField(
        "OpcUa certificate",
        default="1",
        choices=[("0", "No change"), ("1", "Generate new")],
        description="Following files will be overwritten:<ul><li>{}</li><li>{}</li><li>{}</li><li>{}</li></ul>".format(
            _opcua_pem_cert, _opcua_pem_key, _opcua_der_cert, _opcua_der_key
        ),
    )

    cn = StringField(
        "Common name",
        default=default["cn"],
        validators=_validate_dns,
        render_kw={"placeholder": "Hostname, DNS, IP-address or leave it blank"},
    )
    days = IntegerField("Days valid", default=7300)
    basicConstraints = StringField(
        "basicConstraints",
        default=default["basicConstraints"],
        validators=_validate_cmd,
    )
    keyUsage = StringField(
        "keyUsage", default=default["keyUsage"], validators=_validate_cmd
    )
    extendedKeyUsage = StringField(
        "extendedKeyUsage",
        default=default["extendedKeyUsage"],
        validators=_validate_cmd,
    )
    uri_1 = StringField("URI.1", default=default["urn.1"], validators=_validate_url)
    uri_2 = StringField("URI.2", default="", validators=_validate_url)
    uri_3 = StringField("URI.3", default="", validators=_validate_url)
    dns_1 = StringField("DNS.1", default=default["dns.1"], validators=_validate_dns)
    dns_2 = StringField("DNS.2", default="", validators=_validate_dns)
    dns_3 = StringField("DNS.3", default="", validators=_validate_dns)
    ip_1 = StringField("IP.1", default=default["ip.1"], validators=_validate_ip)
    ip_2 = StringField("IP.2", default=default["ip.2"], validators=_validate_ip)
    ip_3 = StringField("IP.3", default=default["ip.3"], validators=_validate_ip)
    ip_4 = StringField("IP.4", default=default["ip.4"], validators=_validate_ip)
    ip_5 = StringField("IP.5", default=default["ip.5"], validators=_validate_ip)
    subjectAltName = HiddenField("subjectAltName:")
    current_password = PasswordField("Current password")

    @staticmethod
    def validate_current_password(form, field):
        validators.DataRequired()(form, field)
        if not utils.check_user_and_pass(
            current_app, flask_login.current_user.id, field.data
        ):
            raise validators.ValidationError("Invalid password")


class SecurityCertificatesView(MyBaseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        conf_ok = utils.can_generate_certs()
        form = SecurityCertificatesForm(request.form)

        if request.method == "POST":
            if form.validate():
                res = ""
                if int(form.gen_webadmin.data):
                    res += utils.generate_overwrite_certificates(
                        _webadmin_pem_cert,
                        _webadmin_pem_key,
                        _webadmin_der_cert,
                        _webadmin_der_key,
                        form.cn.data,
                        form.days.data,
                    )
                if int(form.gen_opcua.data):
                    res += utils.generate_overwrite_certificates(
                        _opcua_pem_cert,
                        _opcua_pem_key,
                        _opcua_der_cert,
                        _opcua_der_key,
                        form.cn.data,
                        form.days.data,
                        1,
                        [form.uri_1.data, form.uri_2.data, form.uri_3.data],
                        [form.dns_1.data, form.dns_2.data, form.dns_3.data],
                        [
                            form.ip_1.data,
                            form.ip_2.data,
                            form.ip_3.data,
                            form.ip_4.data,
                            form.ip_5.data,
                        ],
                        form.basicConstraints.data,
                        form.keyUsage.data,
                        form.extendedKeyUsage.data,
                    )
                if res:
                    flash(res, category="warning")
                else:
                    flash("New certs generated successfully", category="success")
            else:
                flash("All fields not verified", category="error")

        return self.render("security/certificates.html", conf_ok=conf_ok, form=form)

    def is_accessible(self):
        return self.has_role("admin")
