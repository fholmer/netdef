import flask_login
from flask import Flask, abort, redirect, request, url_for
from flask_admin import BaseView, expose, helpers, model


class MyBaseView(BaseView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)
        
    def has_role(self, roles):
        return flask_login.current_user.is_authenticated and flask_login.current_user.has_role(roles)
