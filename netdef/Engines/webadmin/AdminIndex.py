import binascii
import os

import flask_admin
import flask_login
from flask import current_app, redirect, request, url_for
from flask_admin import expose, helpers
from wtforms import fields, form, validators

from ... import __version__ as version
from .. import utils


def shutdown_server():
    func = current_app.config.get("server.shutdown")
    if func is None:
        func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Cannot shutdown. Not running with the Werkzeug Server")
    func()


class MyAdminIndexView(flask_admin.AdminIndexView):
    restarting = 0
    shuttingdown = 0

    @expose("/")
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        else:
            return redirect("/admin/home/")
        # return self.render(self._template, version=version)

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            flask_login.login_user(user)

        if flask_login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        self._template_args["form"] = form
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        flask_login.logout_user()
        return redirect(url_for(".index"))

    @expose("/restart/")
    def restart_view(self):
        shared = current_app.config["SHARED"]
        shared.restart_on_exit = True
        self.restarting = 1
        return redirect(url_for(".command_result_view"))

    @expose("/command_result/")
    def command_result_view(self):
        if self.restarting > 0:
            shutdown_server()
            return self.render("tools/restart_timer.html")

        elif self.shuttingdown > 0:
            shutdown_server()
            return "Shutting down ..."

        else:
            return redirect(url_for(".index"))

    @expose("/shutdown/")
    def shutdown_view(self):
        shared = current_app.config["SHARED"]
        shared.restart_on_exit = False
        self.shuttingdown = 1
        return redirect(url_for(".command_result_view"))


class User(flask_login.UserMixin):
    def __init__(self, userid, roles):
        self.id = userid
        if isinstance(roles, set):
            self.roles = roles
        elif isinstance(roles, (list, tuple)):
            self.roles = set(roles)
        elif isinstance(roles, str):
            self.roles = {roles}
        else:
            self.roles = set()

    def has_role(self, roles):
        if isinstance(roles, set):
            return self.roles.issuperset(roles)
        elif isinstance(roles, (list, tuple)):
            return self.roles.issuperset(set(roles))
        elif isinstance(roles, str):
            return self.roles.issuperset({roles})
        return False


class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError("Invalid user")

        if not utils.check_user_and_pass(
            current_app, self.login.data, self.password.data
        ):
            raise validators.ValidationError("Invalid password")

    def get_user(self):
        admin_users = current_app.config["ADMIN_USERS"]
        if self.login.data in admin_users.keys():
            user_info = admin_users[self.login.data]
            user = User(self.login.data, user_info["roles"])
            return user
        return None
