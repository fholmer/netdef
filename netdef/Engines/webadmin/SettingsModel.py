from flask import current_app
from flask_admin import model
from wtforms import form, fields
from . import Views
from .MyBaseView import MyBaseView

@Views.register("Settings")
def setup(admin):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_settings_on = config(section, "settings_on", 1)
    if webadmin_settings_on:
        admin.add_view(
            SettingsModelView(
                SettingsModel,
                name='Settings'))

class SettingsModelForm(form.Form):
    section = fields.StringField("section")
    key = fields.StringField("key")
    value = fields.StringField("value")

class SettingsModel():
    __slots__ = ("section", "key", "value")
    def __init__(self, section, key, value):
        self.section = section
        self.key = key
        self.value = value
    def __str__(self):
        return (self.section + " " + self.key + " " + self.value)

class SettingsModelView(MyBaseView, model.BaseModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ('section', 'key', 'value')
    column_sortable_list = ()
    column_searchable_list = ('key')
    form = SettingsModelForm

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        shared = current_app.config['SHARED']
        settings_full_list = shared.config.get_full_list()
        settings = [self.model(section, key, value) for section, key, value in settings_full_list]

        if search:
            search = search.lower()
            settings = [setting for setting in settings if str(setting).lower().find(search) >= 0]

        settings = list(settings)
        total = len(settings)
        if not page_size:
            page_size = self.page_size
        results = self.sampling(settings, page * page_size, page_size)
        return total, results

    def init_search(self):
        return True

    def get_pk_value(self, model_):
        return 'key'

    @staticmethod
    def sampling(selection, offset=0, limit=None):
        return selection[offset:(limit + offset if limit is not None else None)]