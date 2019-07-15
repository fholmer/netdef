from . import SharedConfig, SharedQueues, SharedSources, SharedExpressions

class Shared():
    """
    Shared memory for the application.
    This is the class of the *shared* instance that is passed to all
    controllers, rules, engines and expressions. You will use this class to
    read configs, get message queues etc.

    :param str identifier: a unique identifier for this app.
    :param str install_path: Full filepath to application package location
    :param str proj_path: Full filepath to project location
    :param str default_config_string: initial config text for :class:`netdef.Shared.SharedConfig.Config`
    
    """
    def __init__(self, identifier, install_path, proj_path, default_config_string):
        self.config = SharedConfig.Config(identifier, install_path, proj_path, default_config_string)
        self.queues = SharedQueues.SharedQueues(self.config.config("queues", "maxsize", 0))
        self.sources = SharedSources.SharedSources()
        self.expressions = SharedExpressions.SharedExpressions()
        self.restart_on_exit = False
