import logging
import csv
import pathlib

from . import BaseRule, Rules

SourceInfo = BaseRule.SourceInfo
ExpressionInfo = BaseRule.ExpressionInfo

log = logging.getLogger("CSVRule")
NAME = "CSVRule"

log.debug("Loading module")

@Rules.register(NAME)
class CSVRule(BaseRule.BaseRule):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        log.info("init")

    def setup(self):
        "Parse config files"
        log.info("Running setup")
        for name, active in self.shared.config.get_dict(NAME).items():
            if int(active):
                self.setup_csv_rule(name)
        log.info("Done parsing")
        self.setup_done()

    def setup_csv_rule(self, name):
        """
            Parse CSV file. 
        """
        log.info("loading %s", name)
        abs_root = self.shared.config("proj", "path")
        rel_pyfile = self.shared.config(name, "py").strip('"')
        rel_csvfile = self.shared.config(name, "csv").strip('"')
        encoding = self.shared.config(name, "encoding", "").strip('"') or None

        log.info(rel_pyfile)
        log.info(rel_csvfile)

        expression_module = self.get_module_from_string(rel_pyfile, __package__, abs_root, self.name, name)

        abs_csvfile = str(pathlib.Path(abs_root).joinpath(rel_csvfile))

        start_of_csv = 0

        with open(abs_csvfile, encoding=encoding) as csvfile:
            # support the excel spesific sep= header
            firstline = csvfile.readline()
            if firstline.startswith("sep="):
                start_of_csv = csvfile.tell()

            csvfile.seek(start_of_csv)
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(start_of_csv)
            reader = csv.reader(csvfile, dialect)
            headers = next(reader)
            headers = list(h for h in headers if h)

            expression_count = 0
            source_count = 0
            for header in headers:
                source_name, controller_name = self.source_and_controller_from_key(header)
                self.add_new_parser(source_name, controller_name)

            for row in reader:
                expression_count += 1
                source_info_list = [SourceInfo(header, column) for header, column in zip(headers, row)]

                expr_info = ExpressionInfo(expression_module, source_info_list)
                source_count += self.add_new_expression(expr_info)
            
            self.update_statistics(self.name + "." + name, 0, expression_count, source_count)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        log.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # dispatch handle_* functions
        log.info("Stopped")

    def handle_run_expression(self, incoming):
        expressions = self.get_expressions(incoming)
        #log.debug("Received %s. Found expressions %s",incoming.key, len(expressions))
        if expressions:
            self.send_expressions_to_engine(incoming, expressions)
        #for expression in expressions:
        #    expression.execute()
