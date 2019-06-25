import os
from netdef.Controllers import Controllers
from netdef.Sources import Sources
from netdef.Rules import Rules
from netdef.Engines import ThreadedWebGuiEngine
from netdef.Shared import Shared
from netdef.utils import setup_logging, handle_restart
from . import defaultconfig

def main():
    # init shared-module
    try:
        install_path = os.path.dirname(__file__)
        proj_path = os.getcwd()
        config_string = defaultconfig.default_config_string
        shared = Shared.Shared("First-App", install_path, proj_path, config_string)
    except ValueError as error:
        print(error)
        raise SystemExit(1)

    # configure logging
    setup_logging(shared.config)

    controllers = Controllers.Controllers(shared)
    controllers.load([__package__, 'netdef'])

    sources = Sources.Sources(shared)
    sources.load([__package__, 'netdef'])

    rules = Rules.Rules(shared)
    rules.load([__package__, 'netdef'])

    # the engine connects webadmin, controllers, sources and rules.
    engine = ThreadedWebGuiEngine.ThreadedWebGuiEngine(shared)
    engine.add_controller_classes(controllers)
    engine.add_source_classes(sources)
    engine.add_rule_classes(rules)
    engine.load([__package__, 'netdef'])

    engine.init()
    engine.start()
    engine.block() # until ctrl-c or SIG_TERM
    engine.stop()

    # if restart-button in webadmin is pressed:
    handle_restart(shared, engine)

main()
