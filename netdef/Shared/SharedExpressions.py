class ExpressionInstances():
    def __init__(self):
        self.items = []
        self.items_by_reference = {}

    def add_expression(self, item):
        self.items.append(item)

    def add_expression_in_source_ref(self, ref, expression):
        if ref in self.items_by_reference:
            self.items_by_reference[ref].append(expression)
        else:
            self.items_by_reference[ref] = [expression]

    def get_expressions_by_source_ref(self, ref):
        return self.items_by_reference[ref]

    def has_source_ref(self, ref):
        return ref in self.items_by_reference

    def has_expression_in_source_ref(self, ref, expression):
        return expression in self.items_by_reference[ref]

class SharedExpressions():
    instances = ExpressionInstances()
