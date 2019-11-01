import win32serviceutil
import win32service
import win32console
import servicemanager
import pathlib
import os
import sys
from multiprocessing import Process, freeze_support
import traceback

freeze_support()

class GenericApplicationService(win32serviceutil.ServiceFramework):
    application = None
    
    def __init__(self, args):
        super().__init__(args)
        self.running = False
        self.process = None
        
    def SvcStop(self):
        self.running = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        try:
            pids = win32console.GetConsoleProcessList()
        except:
            pids = tuple()
        try:
            pid = self.process.pid

            if not pid in pids:
                win32console.AttachConsole(self.process.pid)

            win32console.GenerateConsoleCtrlEvent(
                win32console.CTRL_C_EVENT,
                self.process.pid
            )

            if not pid in pids:
                win32console.FreeConsole()
        except:
            servicemanager.LogErrorMsg(traceback.format_exc())

    def SvcDoRun(self):
        self.running = True
        #self.application()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        while self.running:
            #if self.process:
            #    logger.info("Restarting")
            self.process = Process(target=self.application)
            self.process.start()
            try:
                self.process.join()
            except KeyboardInterrupt:
                pass

        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED,
                              (self._svc_name_, ''))

def get_service(svc_name, exe_name, app_callback, template_callback=None):
    """
    .. note::
        This function is only implemented for Windows and Systemd based linux
        distributions
    
    Returns the Service-class to use as argument in :func:`run_service`

    :param svc_name: name of the service
    :param exe_name: filename of the service
    :param app_callback: a function that will start your application
    :param template_callback: a function that returns template config
    :return: :class:`GenericApplicationService`

    Example::

        from netdef.service import get_service, run_service

        def run_app():
            from . import main

        def get_template_config():
            from . import defaultconfig
            return defaultconfig.template_config_string

        application_service = get_service("First-App", "First-App-Service", run_app, get_template_config)
        run_service(application_service)
    """

    if not pathlib.Path(exe_name).suffix:
        exe_name = str(pathlib.Path(exe_name).with_suffix('.exe'))

    class ApplicationService(GenericApplicationService):
        _svc_name_ = svc_name
        _svc_display_name_ = svc_name
        _exe_name_ = exe_name
        _exe_args_ = ""
        application = staticmethod(app_callback)
    return ApplicationService

def run_service(app_service_class):
    """
    .. note::
        This function is only implemented for Windows and Systemd based linux
        distributions

    :param app_service_class: service class from :func:`get_service`

    Create an instance of `app_service_class` and run as service

    Example::

        from netdef.service import get_service, run_service

        def run_app():
            from . import main

        def get_template_config():
            from . import defaultconfig
            return defaultconfig.template_config_string

        application_service = get_service("First-App", "First-App-Service", run_app, get_template_config)
        run_service(application_service)
    """
    
    if "-r" in sys.argv:
        proj_path = pathlib.Path(sys.argv[-1]).expanduser().absolute()
        os.chdir(str(proj_path))
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(app_service_class)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        proj_path = pathlib.Path(os.curdir).expanduser().absolute()
        app_service_class._exe_args_ = '-r "' + str(proj_path) + '"'
        win32serviceutil.HandleCommandLine(app_service_class)

