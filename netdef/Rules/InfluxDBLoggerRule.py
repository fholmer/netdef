import logging
import pathlib
from netdef.Rules import BaseRule, Rules
from netdef.Interfaces.InfluxDBLoggerInterface import InfluxDBLoggerInterface

@Rules.register("InfluxDBLoggerRule")
class InfluxDBLoggerRule(BaseRule.BaseRule):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")
        
        config = self.shared.config.config
        self.auto_logging_on = config(self.name, "auto_logging_on", 1)

    def setup(self):
        self.logger.info("Running setup")

    def setup_auto_logging(self):

        def expression_func(something, dblogger):
            if something.new or something.update:
                _val = InfluxDBLoggerInterface.make(
                    something.key,
                    something.instance.source,
                    something.instance.rule,
                    something.instance.controller,
                    something.value,
                    something.instance.source_time,
                    something.instance.status_code
                )
                dblogger.set = _val

        source_count = 0
        exp_count = 0

        items = [item for item in self.shared.sources.instances.items]

        for item in items:
            source_count += self.add_new_expression(
                BaseRule.ExpressionInfo(
                    BaseRule.Expression(expression_func, pathlib.Path(__file__).name),
                    [
                        BaseRule.SourceInfo(item.source, item.key, item.controller),
                        BaseRule.SourceInfo("InfluxDBLoggerSource", item.key, "InfluxDBLoggerController")
                    ]
                )
            )
            exp_count += 1
        self.update_statistics(self.name + ".auto_logging", 0, exp_count, source_count)

    def run(self):
        if self.auto_logging_on:
            self.logger.info("Setup autologging")
            self.setup_auto_logging()

        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() #  dispatch handle_* functions
        self.logger.info("Stopped")

    def handle_run_expression(self, incoming):
        expressions = self.get_expressions(incoming)
        self.logger.debug("Received %s. Found expressions %s",incoming.key, len(expressions))
        if expressions:
            self.send_expressions_to_engine(incoming, expressions)
