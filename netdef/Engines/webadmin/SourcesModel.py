from flask import current_app
from wtforms import form, fields
from flask_admin import model
from ...Sources.BaseSource import BaseSource
from .MyBaseView import MyBaseView
from . import Views

@Views.register("Sources")
def setup(admin):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_sources_on = config(section, "sources_on", 1)
    if webadmin_sources_on:
        admin.add_view(SourcesModelView(BaseSource, name='Sources'))

class SourcesModelForm(form.Form):
    key = fields.StringField("key")
    rule = fields.StringField("rule")
    source = fields.StringField("source")
    controller = fields.StringField("controller")
    value = fields.StringField("value")
    status_code = fields.StringField("status_code")
    source_time = fields.DateTimeField("source_time")

class SourcesModelView(MyBaseView, model.BaseModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ('key', 'rule', 'source', 'controller', 'value_as_string', 'status_code', 'source_time')
    column_sortable_list = ()
    column_searchable_list = ('key', 'rule', 'source', 'controller', 'value')
    form = SourcesModelForm

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        shared = current_app.config['SHARED']

        if search:
            search = search.lower()
            sources = (item for item in shared.sources.instances.items if str(item).lower().find(search) >= 0)
            sources = list(sources)
        else:
            sources = shared.sources.instances.items

        total = len(sources)

        if not page_size:
            page_size = self.page_size

        results = self.sampling(sources, page * page_size, page_size)
        # print(len(results), total, page, page_size, search)
        return total, results

    def init_search(self):
        return True

    def get_pk_value(self, model_):
        return 'key'
        
    @staticmethod
    def sampling(selection, offset=0, limit=None):
        return selection[offset:(limit + offset if limit is not None else None)]