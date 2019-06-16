import sys
import datetime
import subprocess
import platform
import pathlib
import psutil
from flask import current_app, stream_with_context, Response
from flask_admin import expose
from .MyBaseView import MyBaseView
from . import Views

from ... import __version__ as version

APP_STARTUP = datetime.datetime.utcnow()
SYS_STARTUP = datetime.datetime.utcfromtimestamp(psutil.boot_time())

@Views.register("Home")
def setup(admin, view=None):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_tools_on = config(section, "home_on", 1)

    if webadmin_tools_on:
        if not view:
            view = Home(name='Home', endpoint='home')
        admin.add_view(view)

        #replace "home" in menu if it already exists
        if hasattr(admin, "_menu"):
            if admin._menu:
                if admin._menu[0].name.lower() == "home":
                    del admin._menu[0]


class Home(MyBaseView):
    @expose("/")
    def index(self):
        now = datetime.datetime.utcnow()
        app_diff = now - APP_STARTUP
        sys_diff = now - SYS_STARTUP
        return self.render(
            'home.html',
            version=version
        )
