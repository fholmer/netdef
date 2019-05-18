import os
if os.name == "nt":
    from netdef.windows_service import get_service, run_service
else:
    def get_service(*args, **kwargs):
        raise NotImplementedError
    def run_service(*args, **kwargs):
        raise NotImplementedError
