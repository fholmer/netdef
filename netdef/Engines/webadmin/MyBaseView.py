from flask import Flask, url_for, redirect, request, abort

from flask_admin import helpers, expose, model, BaseView
import flask_login

class MyBaseView(BaseView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)
        
    def has_role(self, roles):
        return flask_login.current_user.has_role(roles)
