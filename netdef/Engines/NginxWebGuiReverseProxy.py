import waitress
import logging
from .ThreadedWebGuiEngine import ThreadedWebGuiEngine

log = logging.getLogger("NginxReverseProxy")
log.info("Enter threaded web gui nginx reverse proxy engine")

class NginxReverseProxy(ThreadedWebGuiEngine):
    def block(self):
        # main-funksjonen avslutter når denne funksjonen returnerer
        log.info("run web interface")
        section = "webadmin"

        config = self.shared.config.config
        host = config(section, "host", "")
        port = config(section, "port", 8000)
        log.info("%s %s", host, port)

        # denne klassen tvinger asyncore til å stoppe.
        # denne må registreres i "map" når man ønsker å stoppe
        class _exit_asyncore():
            _counter = 0
            accepting = False
            def readable(self):
                if self._counter > 4: # liten timeout før vi stopper
                    raise KeyboardInterrupt()
                else:
                    self._counter += 1
                return False
            def writable(self):
                return False

        try:
            # denne dict-en sendes helt ned til pollefunksjonene i asyncore og
            # kan av denne grunn benyttes til å stoppe webserver
            _map = {}
                        
            def shutdown():
                #server.task_dispatcher.shutdown(timeout=1)
                _map["exit"] = _exit_asyncore()

            # gjør shutdown-funksjonen tilgjengelig for websidene i AdminIndex.py
            self.app.config["server.shutdown"] = shutdown

            # her startes webserveren, denne blokkerer til ctrl-c mottas
            server = waitress.create_server(self.app, host=host, port=port, map=_map)
            server.run()

        except KeyboardInterrupt:
            pass
