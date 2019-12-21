from unittest.mock import Mock
from netdef.Controllers import SystemMonitorController

def test_get_clean_mount_point_name():
    assert "no change" == \
        SystemMonitorController.get_clean_mount_point_name("no change")

    assert "root.forward.slash.test" == \
        SystemMonitorController.get_clean_mount_point_name(
            "/forward/slash/test/"
        )

    assert "C" == \
        SystemMonitorController.get_clean_mount_point_name(
            "C:\\"
        )

NAME = "SystemMonitorController"
CTRL = SystemMonitorController.SystemMonitorController
def test_init_():
    shared = Mock()
    conf = {
        "oldnew_comparision":0,
        "memory_poll_interval":601,
        "cpu_poll_interval":11,
        "general_poll_interval":12,
        "disk_monitor_on":1,
        "disk_poll_interval":61,
    }
    def get_conf(a,b,c):
        return conf[b]
        
    shared.config.config = get_conf

    ctl = CTRL(NAME, shared)

    assert ctl.oldnew == 0
    assert ctl.memory_poll_interval == 601
    assert ctl.cpu_poll_interval == 11
    assert ctl.poll_interval == 12
    assert ctl.disk_monitor_on == 1
    assert ctl.disk_poll_interval == 61
    assert isinstance(ctl.data_items, dict)
    assert isinstance(ctl.internal_sources, dict)
