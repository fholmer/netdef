import logging
import pathlib
import configparser
import re
from . import BaseRule, Rules

SourceInfo = BaseRule.SourceInfo
ExpressionInfo = BaseRule.ExpressionInfo

compile_parsers = re.compile(r"(?P<source>\w+)")
compile_arguments = re.compile(r"(?P<source>\w+)\((?P<key>([^()])*)\)")

NAME = "INIRule"

@Rules.register(NAME)
class INIRule(BaseRule.BaseRule):
    """
    .. caution:: Development Status :: 4 - Beta

    """

    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")

    def setup(self):
        "Parse config files"
        self.logger.info("Running setup")
        for name, rel_ini_file in self.shared.config.get_dict(NAME).items():
            if rel_ini_file:
                self.setup_ini_rule(name, rel_ini_file)
        self.logger.info("Done parsing")
        self.setup_done()

    def setup_ini_rule(self, name, rel_inifile):
        "parse given ini-file"
        self.logger.info("loading %s", name)
        abs_root = self.shared.config("proj", "path")
        rel_inifile = rel_inifile.strip('"')

        # parse ini
        abs_inifile = str(pathlib.Path(abs_root).joinpath(rel_inifile))
        encoding = None # TODO: parse from config

        ini_object = configparser.ConfigParser()
        ini_object.read(abs_inifile)

        expression_count = 0
        source_count = 0

        for section in ini_object.sections():
            if not ini_object.getint(section, "on", fallback=1):
                continue

            self.logger.info("loading section: %s", section)

            parser_string = ini_object.get(section, "parsers", fallback="")
            parsers = []

            for match in compile_parsers.finditer(parser_string):
                parsers.append(match.group("source"))

            for _source in parsers:
                source_name, controller_name = self.source_and_controller_from_key(_source)
                self.add_new_parser(source_name, controller_name)

            _module = ini_object.get(section, "module", fallback=None)
            _kwargs = {}

            if not _module:
                self.logger.error("module= is missing in [%s]", section)
                continue

            _expression = ini_object.get(section, "expression", fallback=None)
            if _expression:
                    _kwargs["func"] = _expression

            _setup = ini_object.get(section, "setup", fallback=None)
            if _setup:
                _kwargs["setup"] = _setup

            arguments_string = ini_object.get(section, "arguments", fallback="")
            arguments = arguments_string.splitlines()

            for args_line in arguments:
                if args_line:
                    source_info_list = []
                    for match in compile_arguments.finditer(args_line):
                        source_info_list.append(
                            SourceInfo(match.group("source"), match.group("key"))
                        )
                    expression_count += 1
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
