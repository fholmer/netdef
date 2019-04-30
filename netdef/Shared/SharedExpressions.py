class ExpressionInstances():
    def __init__(self):
        self.items = []

    def add_expression(self, item):
        self.items.append(item)

class SharedExpressions():
    instances = ExpressionInstances()
