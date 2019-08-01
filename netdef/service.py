import os
import shutil

__all__ = ['get_service', 'run_service']

service_type = "none"
if os.name == "posix":
    if shutil.which("systemctl"):
        service_type = "systemd"
elif os.name == "nt":
    service_type = "windows"

if service_type =="systemd":
    from netdef.systemd_service import get_service, run_service
elif service_type == "windows":
    from netdef.windows_service import get_service, run_service
else:
    def get_service(*args, **kwargs):
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
        raise NotImplementedError

    def run_service(*args, **kwargs):
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
        raise NotImplementedError
