1.0.4-dev1
==========

2019-07-21

**Enhancements**

- ModbusServerController: get modbus framer by calling self.get_framer
- Added FloatInterface and StringInterface
- Display a 10 second restart timer in webadmin on restart
- InternalController: config entry send_init_event trigger event at startup
- Added an experimental yaml parser
- Added an experimental ini parser
- Source value can be changed from webadmin --> Sources --> Edit

**Bug fixes**

- OPCUAServerController: Fixed a varianttype bug
- Fixed pyinstaller hook file
- BaseRule is rewritten to store expression info in shared module. This fixes
  a problem with multiple rules sharing same sources.
- Fixed a problem where the name of a controller or rule and module name 
  had to be equal.
- OPCUAClientController: specify security mode in configfile
- OPCUAServerController: reject X509IdentityToken

**Incompatible API changes**

- OPCUAServerController: startup statuscode changed from BadNoData to BadWaitingForInitialData
- BaseRule: rule_name_from_key no longer accept * as a rule name

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
