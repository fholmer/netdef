from wtforms import form, fields
from ...Shared.Internal import Statistics
from .SourcesModel import SourcesModelView
from . import Views

@Views.register("Statistics")
def setup(admin):
    section = "webadmin"
    config = admin.app.config['SHARED'].config.config
    webadmin_statistics_on = config(section, "statistics_on", 1)
    if webadmin_statistics_on:
        admin.add_view(
            StatisticsModelView(
                StatisticsModel,
                name='Statistics'
            )
        )

class StatisticsModelForm(form.Form):
    key = fields.StringField("key")
    value = fields.StringField("value")

class StatisticsModel():
    __slots__ = ("key", "value")
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def __str__(self):
        return (self.key + " " + self.value)

class StatisticsModelView(SourcesModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ('key', 'value')
    column_sortable_list = ()
    column_searchable_list = ('key')
    form = StatisticsModelForm

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        if search:
            search = search.lower()
            sources = [self.model(key, value) for key, value in Statistics.statistics.items() if key.lower().find(search) >= 0]
        else:
            sources = [self.model(key, value) for key, value in Statistics.statistics.items()]
        sources = list(sources)
        total = len(sources)
        if not page_size:
            page_size = self.page_size
        results = self.sampling(sources, page * page_size, page_size)
        return total, results
