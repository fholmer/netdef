from . import SharedConfig, SharedQueues, SharedSources, SharedExpressions

class Shared():
    def __init__(self, indentifier, install_path, proj_path, default_config_string):
        self.config = SharedConfig.Config(indentifier, install_path, proj_path, default_config_string)
        self.queues = SharedQueues.SharedQueues(self.config.config("queues", "maxsize", 0))
        self.sources = SharedSources.SharedSources()
        self.expressions = SharedExpressions.SharedExpressions()
        self.restart_on_exit = False
