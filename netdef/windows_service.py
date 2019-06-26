import win32serviceutil
import win32service
import servicemanager
import pathlib
import os
import sys

class GenericApplicationService(win32serviceutil.ServiceFramework):
    application = None
    
    def __init__(self, args):
        super().__init__(args)
        self.running = True
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        
    def SvcDoRun(self):
        self.running = True
        self.application() 

def get_service(svc_name, exe_name, app_callback):
    """
    .. note::
        This function is only implemented in Windows
    
    Returns the Service-class to use as argument in :func:`run_service`

    :param svc_name: name of the service
    :param exe_name: filename of the service
    :param app_callback: a function that will start your application
    :return: :class:`GenericApplicationService`

    Example::

        from netdef.service import get_service, run_service

        def run_app():
            from . import main

        application_service = get_service("First-App", "First-App-Service.exe", run_app)
        run_service(application_service)
    """
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
        This function is only implemented in Windows

    :param app_service_class: service class from :func:`get_service`

    Create an instance of `app_service_class` and run as service

    Example::

        from netdef.service import get_service, run_service

        def run_app():
            from . import main

        application_service = get_service("First-App", "First-App-Service.exe", run_app)
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

