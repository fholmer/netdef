from flask import current_app
from flask_admin import model
from wtforms import form, fields
from . import Views
from .MyBaseView import MyBaseView
from ..expression.Expression import Expression

@Views.register("ExpressionsView")
def setup(admin):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_settings_on = config(section, "expressions_on", 1)
    if webadmin_settings_on:
        admin.add_view(
            ExpressionsModelView(
                ExpressionsModel,
                name='Expressions'))


class ExpressionsModel():
    def __init__(self, expression):
        self._expression = expression

    @property
    def module_filename(self):
        return self._expression.filename

    @property
    def function_name(self):
        return self._expression.expression.__name__

    @property
    def function_arguments(self):
        return ", ".join("{}({})".format(arg.source, arg.key) for arg in self._expression.args)


class ExpressionsModelForm(form.Form):
    module_filename = fields.StringField("module_filename")
    function_name = fields.StringField("function_name")
    function_arguments = fields.StringField("function_arguments")

class ExpressionsModelView(MyBaseView, model.BaseModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ('module_filename', 'function_name', 'function_arguments')
    column_sortable_list = ()
    column_searchable_list = ('module_filename', 'function_name', 'function_arguments')
    form = ExpressionsModelForm

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        shared = current_app.config['SHARED']

        if search:
            search = search.lower()
            expressions = (self.model(item) for item in shared.expressions.instances.items if str(item).lower().find(search) >= 0)
            expressions = list(expressions)
        else:
            expressions = list(self.model(item) for item in shared.expressions.instances.items)

        total = len(expressions)

        if not page_size:
            page_size = self.page_size

        results = self.sampling(expressions, page * page_size, page_size)
        # print(len(results), total, page, page_size, search)
        return total, results

    def init_search(self):
        return True

    def get_pk_value(self, model_):
        return 'key'
        
    @staticmethod
    def sampling(selection, offset=0, limit=None):
        return selection[offset:(limit + offset if limit is not None else None)]
