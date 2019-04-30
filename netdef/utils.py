import logging
from logging.handlers import RotatingFileHandler
import sys
import os

# for assertion:
from .Shared.SharedConfig import Config
from .Shared.Shared import Shared
from .Engines.BaseEngine import BaseEngine

def setup_logging(config):
    assert isinstance(config, Config)
    
    logglevel = logging.INFO
    loggformat = logging.BASIC_FORMAT
    loggdatefmt = "%Y-%m-%d %H:%M:%S"

    if config:
        logglevel = config.config("logging", "logglevel", logglevel)
        loggformat = config.config("logging", "loggformat", loggformat)
        loggdatefmt = config.config("logging", "loggdatefmt", loggdatefmt)
        loggfile = config.config("logging", "loggfile", "log/application.log")
        to_console = config.config("logging", "to_console", 1)
        to_file = config.config("logging", "to_file", 0)

        handlers = []
        if to_console:
            handlers.append(logging.StreamHandler())
        if to_file:
            handlers.append(RotatingFileHandler(loggfile, maxBytes=10485760, backupCount=10))
    else:
        handlers = None

    logging.basicConfig(handlers=handlers, level=logglevel, format=loggformat, datefmt=loggdatefmt)

    if config:
        def exception_logger(exc_type, exc_value, exc_traceback):
            logging.error("exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.excepthook = exception_logger

        for package_name, level in config.get_dict("logginglevels").items():
            logging.getLogger(package_name).setLevel(int(level))

def handle_restart(shared, engine):
    assert(isinstance(shared, Shared))
    assert(isinstance(engine, BaseEngine))
    # dersom restart-knappen i webadmin er benyttet:
    if shared.restart_on_exit:
        engine.wait() # venter på at alle trådene er stoppet

        if sys.argv[0].endswith('__main__.py'):
            # support restart when "python -m APP"
            args = [sys.executable, '-m', __package__] + sys.argv[1:]
        else:
            # support entry_points from setup.py
            args = sys.argv
        try:
            os.execv(args[0], args)
        except (PermissionError, OSError) as error:
            # support python launcApp.py
            os.execv(sys.executable, [sys.executable] + args)