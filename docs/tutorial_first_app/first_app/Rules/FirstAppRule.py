import logging
import pathlib
from netdef.Rules.utils import import_file
from netdef.Rules import BaseRule, Rules

SourceInfo = BaseRule.SourceInfo
ExpressionInfo = BaseRule.ExpressionInfo

@Rules.register("FirstAppRule")
class FirstAppRule(BaseRule.BaseRule):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")
        self.proj_path = shared.config.config("proj", "path")

    def read_list(self, rel_file):
        full_file = pathlib.Path(self.proj_path).joinpath(rel_file)
        lines = open(str(full_file), "r").readlines() 
        return [l.strip() for l in lines]

    def import_py_file(self, rel_file):
        full_file = pathlib.Path(self.proj_path).joinpath(rel_file)
        nice_name = full_file.name
        return import_file(str(full_file), self.name, nice_name)

    def setup(self):
        self.logger.info("Running setup")
        self.setup_commands()
        self.logger.info("Done parsing")

    def setup_commands(self):
        command_expression_module = self.import_py_file("config/command_rule.py")
        command_list = self.read_list("config/command_rule.txt")

        source_count = 0
        for command in command_list:
            source_count += self.add_new_expression(
                ExpressionInfo(
                    command_expression_module,
                    [
                        SourceInfo("InternalSource", "generic"),
                        SourceInfo("SubprocessSource", command)
                    ]
                )
            )
        self.update_statistics(self.name + ".commands", 0, 1, source_count)

    def run(self):
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() #  dispatch handle_* functions
        self.logger.info("Stopped")

    def handle_run_expression(self, incoming, value, source_time, status_code):
        expressions = self.get_expressions(incoming)
        self.logger.debug("Received %s. Found expressions %s",incoming.key, len(expressions))
        if expressions:
            self.send_expressions_to_engine(incoming, expressions, value, source_time, status_code)