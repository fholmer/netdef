1.0.7.dev1
==========

**Enhancements**

- SecurityCertificatesView: Added OpcUa certs
- Controllers: call setup-function in module if found at startup
- Rules: call setup-function in module if found at startup
- Sources: call setup-function in module if found at startup
- BaseSource: call setup-function in source instance if found at startup
- Added testutils.MockShared

**Bug fixes**

- Values from controller is frozen before RUN_EXPRESSION is sendt.
- CommTestSource: remove url_path from host

**Incompatible API changes**

- handle_run_expression function in BaseRule now have 4 required arguments.
  All custom rules have to be updated.


1.0.6
=====

2020-02-28

**Enhancements**

- Webadmin: Added role based user table
- Added testutils.MockExpression to simplify testing of expressions
- Added: InfluxDBLogger
- Improved ModbusClientController
- BaseController: Improved message queue helper function
- InternalController: Improved persistent storage
- OPCUAServerController: added config for auto_build_folders
- ModbusServerController: new option: daemon_threads

**Bug fixes**

- ModbusServerController: Attempt to bind to socket for three minutes before
  throwing exception.

**Incompatible API changes**

- MQTTDataMessageController: renamed from MQTTDataAccessController
- Webadmin: [webadmin]user/password keyword has changed.
- InternalController: changed persistent storage filenames

1.0.5
=====

2019-11-07

**Enhancements**

- OPCUAClientController: Improved configuration
- OPCUAServerController: Added legacy support for basic128rsa15 and basic256.
- Webadmin: Added SecurityWebadminView and SecurityCertificatesView
- ModbusServerController: Attempt to bind to socket for one minute before
  throwing exception. (Handle CLOSE_WAIT state)

**Bug fixes**

- Webadmin: Changed height of file edit textarea to 20 rows
- Webadmin: Fixed routing.BuildError when you don't have the permission
  to access the requested resource.
- CSVRule: expression can now be a modulename or a python-file
- Fixed Windows service.
- OPCUAServerController: Fixed TypeError
- OPCUAServerController: Only add subscription if exists

**Incompatible API changes**

- InternalController: changed persistent storage filenames

1.0.4
=====

2019-08-19

**Enhancements**

- ModbusServerController: get modbus framer by calling self.get_framer
- Added FloatInterface and StringInterface
- Display a 10 second restart timer in webadmin on restart
- InternalController: config entry send_init_event trigger event at startup
- Added an experimental yaml parser
- Added an experimental ini parser
- Source value can be changed from webadmin --> Sources --> Edit
- Added create_interface function to expression arguments
- Added persistent storage to InternalController
- Added new message type APP_STATE
- Added Alpha version of ConcurrentWebRequestController
- Added simple installer for Systemd services

**Bug fixes**

- OPCUAServerController: Fixed a varianttype bug
- Fixed pyinstaller hook file
- BaseRule is rewritten to store expression info in shared module. This fixes
  a problem with multiple rules sharing same sources.
- Fixed a problem where the name of a controller or rule and module name 
  had to be equal.
- OPCUAClientController: specify security mode in configfile
- OPCUAServerController: reject X509IdentityToken
- OPCUAServerController: force timestamp on values (from clients) where timestamp is none

**Incompatible API changes**

- OPCUAServerController: startup statuscode changed from BadNoData to BadWaitingForInitialData
- BaseRule: rule_name_from_key no longer accept * as a rule name
- BaseController: fetch_one_incoming returns tuple

1.0.3
=====

2019-06-16

**Enhancements**

- SystemMonitorController: monitor disk partition usage
- Display update options in webadmin --> Tools --> Upgrade
- BaseRule: call setup-function in expressions if found at startup
- Added docs
- OPCUAServerController: OPCUA controller will set statuscode BadNoData on startup.
- Added BaseAsyncController
- Webadmin: / redirects to admin page. /admin redirects to /admin/home.
- Allow for existing flask apps to be integrated in Webadmin

**Bug fixes**

- Added requirements and missing interface
- Added extendable blocks in html templates
- Tools.setup got a view argument

**Incompatible API changes**

- Expression: interface attribute have been removed from expressions arguments

1.0.2
=====

2019-05-25

**Enhancements**

- Added support for Windows services. require pywin32 package on windows

1.0.1
=====

2019-05-17

**Enhancements**

- Added CrontabController
- Added MQTTDataAccessController
- Added RESTJsonController
- Added SystemMonitorController
- Added simple user/pass to OPCUAServerController

**Bug fixes**

- Fixed netdef entrypoint

1.0.0
=====

2019-04-30

- First public release
