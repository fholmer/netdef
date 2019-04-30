from flask import Flask, url_for, redirect, request

from flask_admin import helpers, expose, model, BaseView
import flask_login

class MyBaseView(BaseView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/', next=request.url))