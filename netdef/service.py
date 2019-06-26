import os
if os.name == "nt":
    from netdef.windows_service import get_service, run_service
else:
    def get_service(*args, **kwargs):
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
        raise NotImplementedError

    def run_service(*args, **kwargs):
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
        raise NotImplementedError
