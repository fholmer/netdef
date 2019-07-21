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
    SourcesModelView.can_edit = True if config(section, "sources_can_edit", 1) else False
    if webadmin_sources_on:
        admin.add_view(SourcesModelView(BaseSource, name='Sources'))

class SourcesModelForm(form.Form):
    key = fields.StringField("key", render_kw={'readonly': True})
    source = fields.StringField("source", render_kw={'readonly': True})
    source_datatype = fields.StringField("source_datatype", render_kw={'readonly': True})
    set_value = fields.StringField("set_value", render_kw={'readonly': True})
    set_source_time = fields.StringField("set_source_time", render_kw={'readonly': True})
    set_origin = fields.StringField("set_origin", render_kw={'readonly': True})
    set_status_code = fields.StringField("set_status_code", render_kw={'readonly': True})

    def process(self, *args, **kwargs):
        obj = kwargs.get("obj", args[1])
        if obj:
            if obj.can_set_value_from_string():
                self.set_value.render_kw.clear()
        super().process(*args, **kwargs)

class SourcesModelView(MyBaseView, model.BaseModelView):
    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True
    column_list = ('key', 'rule', 'source', 'controller', 'value_as_string', 'status_code', 'source_time')
    column_sortable_list = ()
    column_searchable_list = ('key', 'rule', 'source', 'controller', 'value')
    column_details_list = ('key', 'rule', 'source', 'controller', 'value_as_string', 'status_code', 'source_time', 'source_datatype', 'get_value', 'get_source_time', 'get_status_code', 'get_origin', 'set_value', 'set_source_time', 'set_status_code', 'set_origin')
    form = SourcesModelForm

    def get_one(self, ref):
        shared = current_app.config['SHARED']
        return shared.sources.instances.get_item_by_ref(ref)

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
        return model_.get_reference()
        
    @staticmethod
    def sampling(selection, offset=0, limit=None):
        return selection[offset:(limit + offset if limit is not None else None)]

    def update_model(self, form, model):
        value = form.set_value.data
        if model.can_set_value_from_string():
            model.set_value_from_string(value, origin="webadmin")
            return True
        return False
