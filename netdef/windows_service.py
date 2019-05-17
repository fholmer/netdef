import win32serviceutil
import win32service
import servicemanager
import pathlib
import os
import sys

class ApplicationService(win32serviceutil.ServiceFramework):
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

def run_service(app_service_class):
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

