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


Default configs
---------------

.. list-table:: General configs
   :header-rows: 1
   :widths: 20 15 15 50
   
   * - Section
     - Key
     - Default
     - Description

   * - general
     - identifier
     - [appident]
     - Name of application.
       
       * **[appident]** -- is the unique name of your
         application. The name have to match in
         order for your application to accept the
         config file.

   * - general
     - version
     - 1 
     - Version of your configfile. If you have to
       break compatibility in the future you can
       bump the config version to reject
       outdated config files

   * - config
     - [unique key]
     - [filename]
     - Name of a configfile to be parsed.

       * **[unique key]** -- is just a unique key
       * **[filepath]** -- is the actual filename.
         File path relative to project folder.
       
       .. code-block:: ini
          :caption: Example

          [config]
          my_conf = config/my_configuration.conf
          more_things = config/more_configs.conf

   * - logging
     - logglevel
     - 20
     - Default logging level for the application

       * **1** -- All
       * **10** -- Debug
       * **20** -- Info
       * **30** -- Warning
       * **40** -- Error
       * **50** -- Critical

   * - logging
     - loggformat
     - %(asctime)-15s
       %(levelname)-9s:
       %(name)-11s:
       %(message)s
     - Logging format for the application

   * - logging
     - loggdatefmt
     - %Y-%m-%d
       %H:%M:%S
     - Date time format

   * - logging
     - to_console
     - 1
     - 
       * **0** -- Suppress output to stdout
       * **1** -- Write output to stdout

   * - logging
     - to_file
     - 0
     - 
       * **0** -- Disable logfile
       * **1** -- Write output to logfile

   * - logging
     - loggfile
     - log/application.log
     - Path to logfile is relative to
       project folder.

   * - logginglevels
     - [module name]
     - 20
     - * **[module name]** is the name of a python module that is using the
         logging module
       
       Values:

       * **1** -- All
       * **10** -- Debug
       * **20** -- Info
       * **30** -- Warning
       * **40** -- Error
       * **50** -- Critical

       .. code-block:: ini
          :caption: Example

          [logginglevels]
          werkzeug = 40
          InternalController = 10

   * - logginglevels
     - werkzeug
     - 40
     - Logging level of werkzeug module is set
       to *warning*

   * - queues
     - maxsize
     - 0
     - Default queue size for all shared queues
       
       * **0** -- No limit
       * **>0** -- Size limit

   * - rules
     - [unique key]
     - 0
     - [unique key] is the unique name of a
       :class:`BaseRule<netdef.Rules.BaseRule>`

       * **0** -- disabled
       * **1** -- enabled

       .. code-block:: ini
          :caption: Example

           [rules]
           CSVRule = 1

   * - controllers
     - [unique key]
     - 0
     - [unique key] is the unique name of a
       :class:`BaseController<netdef.Controllers.BaseController>`
       
       * **0** -- disabled
       * **1** -- enabled
       
       .. code-block:: ini
          :caption: Example

          [controllers]
          InternalController = 1

   * - sources
     - [unique key]
     - 0
     - [unique key] is the unique name of a
       :class:`BaseSource<netdef.Sources.BaseSource>`
       
       * **0** -- disabled
       * **1** -- enabled
       
       .. code-block:: ini
          :caption: Example

          [sources]
          IntegerSource = 1

.. list-table:: Aliases
   :header-rows: 1
   :widths: 20 15 15 50

   * - Section
     - Key
     - Default
     - Description

   * - controller_aliases
     - [unique key]
     - [controllername]
     - Create multiple controller
       instances of same class
       
       .. code-block:: ini
          :caption: Example
        
          [controllers]
          CommTestController = 1
         
          [controller_aliases]
          FastPingController=CommTestController
          SlowPingController=CommTestController

   * - source_aliases
     - [unique key]
     - [sourcename]
     - Create multiple sources based on
       an existing source
       
       .. code-block:: ini
          :caption: Example

          [sources]
          IntegerSource = 1
       
          [source_aliases]
          IntStatusSource = IntegerSource
          IntCommandSource = IntegerSource

.. list-table:: Thread pool configs
   :header-rows: 1
   :widths: 20 15 15 50
   
   * - Section
     - Key
     - Default
     - Description

   * - ExpressionExecutor
     - max_workers
     - [cpu_count * 10]
     - Number of thread pool workers to be
       available in
       :class:`netdef.Engines.ThreadedEngine`

.. config-webadmin-marker-start

.. list-table:: Webadmin
   :header-rows: 1
   :widths: 20 15 15 50

   * - Section
     - Key
     - Default
     - Description

   * - webadmin
     - Config
     - Default
     - Description
     
   * - webadmin
     - host
     - 0.0.0.0
     - Webserver host address
     
   * - webadmin
     - port
     - 8000
     - Webserver tcp port
     
   * - webadmin
     - users.admin.user
     - admin
     - Username
     
   * - webadmin
     - users.admin.password
     - 
     - Plain text password. If password_hash is set
       then this option is ignored.
     
   * - webadmin
     - users.admin.password_hash
     - 
     - Password hash generated with
       ``python -m netdef -ga`` command

   * - webadmin
     - users.admin.roles
     - admin
     - name of user role.
     
   * - webadmin
     - secret_key
     - 
     - Secret flask session key.
       Can be generated with
       ``python -m netdef -ga``
     
   * - webadmin
     - on
     - 1
     - Enable Webadmin.
       
       * **0** -- disabled.
       * **1** -- enabled.
     
   * - webadmin
     - home_on
     - 1
     - Enable :menuselection:`Webadmin-->Home`.
     
   * - webadmin
     - config_on
     - 1
     - Enable :menuselection:`Webadmin-->Config`.
     
   * - webadmin
     - tools_on
     - 1
     - Enable :menuselection:`Webadmin-->Tools`.

   * - webadmin
     - installationrepo_on
     - 1
     - Enable :menuselection:`Webadmin-->Tools-->Upgrade`.

   * - webadmin
     - security_webadmin_on
     - 1 or 0
     - Enable :menuselection:`Webadmin-->Tools-->Webadmin`.

       .. code-block:: ini
       
         [config]
         webadmin_conf=config/webadmin.conf
       
       The default value is 1 if *webadmin_conf* exists in *[config]*

   * - webadmin
     - security_certificates_on
     - 1
     - Enable :menuselection:`Webadmin-->Tools-->Certificates`.
     
   * - webadmin
     - settings_on
     - 1
     - Enable :menuselection:`Webadmin-->Settings`.
     
   * - webadmin
     - sources_on
     - 1
     - Enable :menuselection:`Webadmin-->Sources`.
     
   * - webadmin
     - expressions_on
     - 1
     - Enable :menuselection:`Webadmin-->Expressions`.
     
   * - webadmin
     - statistics_on
     - 1
     - Enable :menuselection:`Webadmin-->Statistics`.
     
   * - webadmin
     - ssl_certificate
     - 
     - File path to ssl certificate.
       Required if ``ssl_on=1``.
     
   * - webadmin
     - ssl_certificate_key
     - 
     - File path to ssl certificate key.
       Required if ``ssl_on=1``.
     
   * - webadmin
     - ssl_on
     - 0
     - Enable https.
     
   * - webadmin_views
     - [viewident]
     - 0
     - [viewident] is the unique name of a
       :class:`MyBaseView<netdef.Engines.webadmin.MyBaseView>`

       * **0** -- disabled.
       * **1** -- enabled.

       .. code-block:: ini
          :caption: Example

          [webadmin_views]
          Home = 1

   * - webadmin_views
     - Home
     - 1
     - Enable Home view.

   * - webadmin_views
     - FileModel
     - 1
     - Enable FileModel view.

   * - webadmin_views
     - SettingsModel
     - 1
     - Enable SettingsModel view.

   * - webadmin_views
     - SourcesModel
     - 1
     - Enable SourcesModel view.

   * - webadmin_views
     - ExpressionsView
     - 1
     - Enable ExpressionsView view.

   * - webadmin_views
     - StatisticsModel
     - 1
     - Enable StatisticsModel view.

   * - webadmin_views
     - Tools
     - 1
     - Enable Tools view.

.. config-webadmin-marker-end


.. list-table:: Upgrade application
   :header-rows: 1
   :widths: 20 15 15 50

   * - Section
     - Key
     - Default
     - Description
     
   * - auto_update
     - on
     - 0
     - 

   * - auto_update
     - no_index
     - 0
     -

   * - auto_update
     - pre_release
     - 0
     -

   * - auto_update
     - force_reinstall
     - 0
     -

   * - auto_update
     - find_links
     - 
     -

   * - auto_update
     - trusted_host
     - 
     - |

   * - auto_update
     - minimal_timeout
     - 0
     -

   * - auto_update
     - package
     - [appident]
     -

Built-in Controllers and Rules
------------------------------

You can look opp the correct :doc:`/api/configs` in API Reference
