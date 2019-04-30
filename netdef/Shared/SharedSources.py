class SourceClasses():
    def __init__(self):
        self.init_items({})

    def init_items(self, items):
        self.items = items

    def add_item(self, source_name, classobj):
        self.items[source_name] = classobj

    def get_item(self, name):
        return self.items[name]


class SourceInstances():
    def __init__(self):
        self.items = []
        self.items_by_reference = {}

    def add_item(self, item):
        if item.get_reference() in self.items_by_reference:
            raise ValueError("Duplicate item: {}".format(item))
        self.items_by_reference[item.get_reference()]=  item
        self.items.append(item)

    def get_item_by_ref(self, ref):
        return self.items_by_reference[ref]

    def has_item_ref(self, ref):
        return ref in self.items_by_reference


class SharedSources():
    """ *classes* inneholder en dict *items* med uinstansierte
        sources-klasser. (nøkkel er navn fra konfig, verdi er klassen)
        Brukes av regelmotor når den parser konfigfiler og skal finne riktig source.

        *instances* inneholder liste over alle sources instanser opprettet av regelmotor.
    """
    classes = SourceClasses()
    instances = SourceInstances()
