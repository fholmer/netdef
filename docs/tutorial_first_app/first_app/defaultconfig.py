template_config_string = \
"""[general]
identifier = First-App
version = 1
"""

default_config_string = \
"""[general]
[config]
[ExpressionExecutor]
[webadmin]
host = 0.0.0.0
port = 8000
user = admin
password = admin

[webadmin_views]

[logging]
logglevel = 20
loggformat = %(asctime)-15s %(levelname)-9s: %(name)-11s: %(message)s
loggdatefmt = %Y-%m-%d %H:%M:%S
to_console = 1
to_file = 1

[logginglevels]
werkzeug = 40

[rules]

[controllers]

[controller_aliases]

[sources]

[source_aliases]
"""
