import logging
import pathlib
from .utils import import_file
from . import BaseRule, Rules

SourceInfo = BaseRule.SourceInfo
ExpressionInfo = BaseRule.ExpressionInfo

@Rules.register("NewTemplateRule")
class NewTemplateRule(BaseRule.BaseRule):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")
        
        config = self.shared.config.config
        self.proj_path = pathlib.Path(config("proj", "path", ".")).absolute()

    def setup(self):
        self.logger.info("Running setup")

        # example:
        self.setup_example()

        # sub rule example:
        for name, active in self.shared.config.get_dict(self.name).items():
            if int(active):
                self.setup_sub_rule(name)
        self.logger.info("Done parsing")
    
    def setup_sub_rule(self, name):
        raise NotImplementedError

    def setup_example(self):
        #example_expression_module = self.import_py_file("config/example_expression.py")

        # config/example_expresion.py:
        # def expression(internal):
        #     if internal.new or internal.update:
        #         print(internal)

        self.add_new_parser("InternalSource")

        source_count = self.add_new_expression(
            ExpressionInfo(
                example_expression_module,
                [
                    SourceInfo("InternalSource", "intern_test_1")
                ]
            )
        )
        self.update_statistics(self.name + ".example", 0, 1, source_count)

    def import_py_file(self, rel_file):
        full_file = pathlib.Path(self.proj_path).joinpath(rel_file)
        nice_name = full_file.name
        return import_file(str(full_file), self.name, nice_name)

    def run(self):
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
        self.logger.info("Stopped")

    def handle_run_expression(self, incoming):
        expressions = self.get_expressions(incoming)
        self.logger.debug("Received %s. Found expressions %s",incoming.key, len(expressions))
        if expressions:
            self.send_expressions_to_engine(incoming, expressions)
