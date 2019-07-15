Configuration
=============

Config files is parsed at startup using the ``configparser`` module. Multiple
strings and files is read in following order:

* (str) mypackage.defaultconfig:default_config_string
* (file) config/default.conf
* (file) config/default. **[osname]** .conf where **osname** is **nt** on
  windows and **posix** on linux.
* (files) all files found in [config] section in default.conf
* (file) config/default.conf.lock

Extended interpolation
----------------------

Extended interpolation is using ``${section:option}`` to denote a value from a
foreign section. Example:

.. code-block:: ini
    :caption: default.conf

    [OPCUAClientController]
    endpoint = opc.tcp://${client:host}:${client:port}/freeopcua/server/
    user = ${client:user}
    password = ${client:password}

    [OPCUAServerController]
    endpoint = opc.tcp://${server:host}:${server:port}/freeopcua/server/
    user = ${server:user}
    password = ${server:password}

    [client]
    host = 10.10.1.13
    port = 4841
    user = CommonUser
    password = 7T-SECRET_PASS-PhsTh7yVpV9jKTShAXcOdL8KmO4m3MUY3EPu7

    [server]
    host = 0.0.0.0
    port = 4841
    user = ${client:user}
    password = ${client:password}

By using extended interpolation in combination with [config] section you can
move application secrets into its own config file:

.. code-block:: ini
   :caption: default.conf

    [config]
    secrets_conf = config/secrets.conf

    [OPCUAClientController]
    endpoint = opc.tcp://${client:host}:${client:port}/freeopcua/server/
    user = ${client:user}
    password = ${client:password}

    [OPCUAServerController]
    endpoint = opc.tcp://${server:host}:${server:port}/freeopcua/server/
    user = ${server:user}
    password = ${server:password}

.. code-block:: ini
   :caption: secrets.conf

    [client]
    host = 10.10.1.13
    port = 4841
    user = CommonUser
    password = 7T-SECRET_PASS-PhsTh7yVpV9jKTShAXcOdL8KmO4m3MUY3EPu7

    [server]
    host = 0.0.0.0
    port = 4841
    user = ${client:user}
    password = ${client:password}


Built-in configs
----------------

.. list-table:: Built-in configs
   :header-rows: 1
   :widths: 5 5 5 85
   
   * - | Section
     - | Key
     - | Default
     - | Description

   * - | general
     - | identifier
     - | [appident]
     - | Name of application.
       | [appident] is the unique name of your
       | application. The name have to match in
       | order for your application to accept the
       | config file.

   * - | general
     - | version
     - | 1 
     - | Version of your configfile. If you have to
       | break compatibility in the future you can
       | bump the config version to reject
       | outdated config files

   * - | config
     - | [unique key]
     - | [filename]
     - | Name of a configfile to be parsed.
       | [unique key] is just a unique key and
       | [filepath] is the actual filename.
       | File path relative to project folder.

   * - | ExpressionExecutor
     - | max_workers
     - | [cpu_count * 10]
     - | Number of thread pool workers to be
       | available in
       | :class:`netdef.Engines.ThreadedEngine`


   * - | logging
     - | logglevel
     - | 20
     - | Default logging level for the application

   * - | logging
     - | loggformat
     - | %(asctime)-15s
       | %(levelname)-9s:
       | %(name)-11s:
       | %(message)s
     - | Logging format for the application

   * - | logging
     - | loggdatefmt
     - | %Y-%m-%d
       | %H:%M:%S
     - | Date time format

   * - | logging
     - | to_console
     - | 1
     - | 1: Write output to stdout
       | 0: Suppress output to stdout

   * - | logging
     - | to_file
     - | 0
     - | 1: Write output to logfile
       | 0: Disable logfile

   * - | logging
     - | loggfile
     - | log/application.log
     - | Path to logfile is relative to
       | project folder.

   * - | logginglevels
     - | werkzeug
     - | 40
     - | Logging level of werkzeug module is set
       | to *warning*

   * - | queues
     - | maxsize
     - | 0
     - | Default queue size for all shared queues
       | 0: No limit

   * - | rules
     - | [unique key]
     - | 0
     - | [unique key] is the unique name of a
       | :class:`netdef.Rules.BaseRule`
       | 1: enabled
       | 0: disabled
       |
       | Example:
       | [rules]
       | CSVRule = 1

   * - | controllers
     - | [unique key]
     - | 0
     - | [unique key] is the unique name of a
       | :class:`netdef.Controllers.BaseController`
       | 1: enabled
       | 0: disabled
       |
       | Example:
       | [controllers]
       | InternalController = 1

   * - | sources
     - | [unique key]
     - | 0
     - | [unique key] is the unique name of a
       | :class:`netdef.Sources.BaseSource`
       | 1: enabled
       | 0: disabled
       |
       | Example:
       | [sources]
       | IntegerSource = 1

   * - | controller_aliases
     - | [unique key]
     - | [controllername]
     - | Create multiple controller
       | instances of same class
       | 
       | Example:
       | 
       | [controllers]
       | CommTestController = 1
       |
       | [controller_aliases]
       | FastPingController=CommTestController
       | SlowPingController=CommTestController

   * - | source_aliases
     - | [unique key]
     - | [sourcename]
     - | Create multiple sources based on
       | an existing source
       |
       | Example:
       |
       | [sources]
       | IntegerSource = 1
       |
       | [source_aliases]
       | IntStatusSource = IntegerSource
       | IntCommandSource = IntegerSource

.. list-table:: Webadmin
   :header-rows: 1
   :widths: 5 5 5 85

   * - | Section
     - | Key
     - | Default
     - | Description

   * - | webadmin
     - | Config
     - | Default
     - | Description
     
   * - | webadmin
     - | host
     - | 0.0.0.0
     - | Webserver host address
     
   * - | webadmin
     - | port
     - | 8000
     - | Webserver tcp port
     
   * - | webadmin
     - | user
     - | admin
     - | Username
     
   * - | webadmin
     - | password
     - | 
     - | Plain text password. If password_hash is set
       | then this option is ignored.
     
   * - | webadmin
     - | password_hash
     - | 
     - | Password hash generated with
       | ``python -m netdef -ga`` command
     
   * - | webadmin
     - | secret_key
     - | 
     - | Secret flask session key.
       | Can be generated with
       | ``python -m netdef -ga``
     
   * - | webadmin
     - | on
     - | 1
     - | Enable Webadmin.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | home_on
     - | 1
     - | Enable Webadmin->Home.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | config_on
     - | 1
     - | Enable Webadmin->Config.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | installationrepo_on
     - | 1
     - | Enable Webadmin->Tools-Update.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | tools_on
     - | 1
     - | Enable Webadmin->Tools.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | settings_on
     - | 1
     - | Enable Webadmin->Settings.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | sources_on
     - | 1
     - | Enable Webadmin->Sources.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | expressions_on
     - | 1
     - | Enable Webadmin->Expressions.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | statistics_on
     - | 1
     - | Enable Webadmin->Statistics.
       | 1: enabled.
       | 0: disabled.
     
   * - | webadmin
     - | ssl_certificate
     - | 
     - | File path to ssl certificate.
       | Required if ssl_on=1.
     
   * - | webadmin
     - | ssl_certificate_key
     - | 
     - | File path to ssl certificate key.
       | Required if ssl_on=1.
     
   * - | webadmin
     - | ssl_on
     - | 0
     - | Enable https. 1: enabled. 0: disabled.
     
   * - | webadmin_views
     - | [viewident]
     - | 0
     - | [viewident] is the unique name of a
       | :class:`netdef.Engines.webadmin.MyBaseView`
       | 1: enabled.
       | 0: disabled.
       | 
       | Example:
       | [webadmin_views]
       | Home = 1

   * - | webadmin_views
     - | Home
     - | 1
     - | Enable Home view.

   * - | webadmin_views
     - | FileModel
     - | 1
     - | Enable FileModel view.

   * - | webadmin_views
     - | SettingsModel
     - | 1
     - | Enable SettingsModel view.

   * - | webadmin_views
     - | SourcesModel
     - | 1
     - | Enable SourcesModel view.

   * - | webadmin_views
     - | ExpressionsView
     - | 1
     - | Enable ExpressionsView view.

   * - | webadmin_views
     - | StatisticsModel
     - | 1
     - | Enable StatisticsModel view.

   * - | webadmin_views
     - | Tools
     - | 1
     - | Enable Tools view.


.. list-table:: Upgrade application
   :header-rows: 1
   :widths: 5 5 5 85

   * - | Section
     - | Key
     - | Default
     - | Description
     
   * - | auto_update
     - | on
     - | 0
     - |

   * - | auto_update
     - | no_index
     - | 0
     - |

   * - | auto_update
     - | pre_release
     - | 0
     - |

   * - | auto_update
     - | force_reinstall
     - | 0
     - |

   * - | auto_update
     - | find_links
     - | 
     - |

   * - | auto_update
     - | trusted_host
     - | 
     - |

   * - | auto_update
     - | minimal_timeout
     - | 0
     - |

   * - | auto_update
     - | package
     - | [appident]
     - |
