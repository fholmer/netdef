import os
from netdef.Controllers import Controllers
from netdef.Sources import Sources
from netdef.Rules import Rules
from netdef.Engines import ThreadedWebGuiEngine
from netdef.Shared import Shared
from netdef.utils import setup_logging, handle_restart
from . import defaultconfig

def main():
    # for å sette opp logging må vi først initiere shared-modulen
    try:
        install_path = os.path.dirname(__file__)
        proj_path = os.getcwd()
        config_string = defaultconfig.default_config_string
        shared = Shared.Shared('APP_IDENT', install_path, proj_path, config_string)
    except ValueError as error:
        print(error)
        raise SystemExit(1)

    # konfigurerer logging basert på konfigfil
    setup_logging(shared.config)

    # importerer kontrollermoduler som er aktivert i konfigfil
    controllers = Controllers.Controllers(shared)
    controllers.load([__package__, 'netdef'])

    # importerer kildeklasser som er aktivert i konfigfil
    sources = Sources.Sources(shared)
    sources.load([__package__, 'netdef'])

    # importerer regelmotorer som er aktivert i konfigfil
    rules = Rules.Rules(shared)
    rules.load([__package__, 'netdef'])

    # motoren som kobler webgrensesnitt, kontrollere, kilder og regler sammen.
    engine = ThreadedWebGuiEngine.ThreadedWebGuiEngine(shared)
    engine.add_controller_classes(controllers)
    engine.add_source_classes(sources)
    engine.add_rule_classes(rules)
    engine.load([__package__, 'netdef'])

    engine.init()
    engine.start()
    engine.block() # blokkerer til ctrl-c eller SIG_TERM mottas
    engine.stop()

    # dersom restart-knappen i webadmin er benyttet:
    handle_restart(shared, engine)

main()
