import logging
import pathlib
import yaml
from . import BaseRule, Rules

SourceInfo = BaseRule.SourceInfo
ExpressionInfo = BaseRule.ExpressionInfo

NAME = "YAMLRule"

@Rules.register(NAME)
class YAMLRule(BaseRule.BaseRule):
    """
    .. danger:: Development Status :: 3 - Alpha
    
    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")

    def setup(self):
        "Parse config files"
        self.logger.info("Running setup")
        for name, rel_yaml_file in self.shared.config.get_dict(NAME).items():
            if rel_yaml_file:
                self.setup_yaml_rule(name, rel_yaml_file)
        self.logger.info("Done parsing")
        self.setup_done()

    def setup_yaml_rule(self, name, rel_yamlfile):
        "parse given yaml-file"
        self.logger.info("loading %s", name)
        abs_root = self.shared.config("proj", "path")
        rel_yamlfile = rel_yamlfile.strip('"')
        self.logger.info(rel_yamlfile)

        # parse yaml
        abs_yamlfile = str(pathlib.Path(abs_root).joinpath(rel_yamlfile))
        encoding = None # TODO: parse from config

        with open(abs_yamlfile, encoding=encoding) as yamlfile:

            yaml_object = yaml.safe_load(yamlfile)

            expression_count = 0
            source_count = 0

            for _parser in yaml_object.get("parsers", []):
                _source = _parser["source"]
                _controller = _parser["controller"] if "controller" in _parser else None
                source_name, controller_name = self.source_and_controller_from_key(_source, _controller)
                self.add_new_parser(source_name, controller_name)

            for _expression in yaml_object.get("expressions", []):
                _module = _expression["module"]
                _kwargs = {}
                _args = _expression["arguments"]
                if "expression" in _expression:
                    _kwargs["func"] = _expression["expression"]
                if "setup" in _expression:
                    _kwargs["setup"] = _expression["setup"]

                expression_count += 1
                source_info_list = [SourceInfo(arg["source"], arg["key"]) for arg in _args]
                expression_module = self.get_module_from_string(_module, __package__, abs_root, self.name, name)
                expr_info = ExpressionInfo(expression_module, source_info_list, **_kwargs)
                source_count += self.add_new_expression(expr_info)
            
            self.update_statistics(self.name + "." + name, 0, expression_count, source_count)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # dispatch handle_* functions
        self.logger.info("Stopped")

    def handle_run_expression(self, incoming):
        expressions = self.get_expressions(incoming)
        if expressions:
            self.send_expressions_to_engine(incoming, expressions)
