from tavern.core import run
from data import extra_cfg,extra_cfg1,extra_cfg2,extra_cfg3,extra_cfg4

def test_conf(list_config):
    for _ in list_config:
        success = run(in_file="test.tavern.yaml",tavern_global_cfg=_)

        if not success:
            print("Error running tests")



test_conf([extra_cfg,extra_cfg1,extra_cfg2,extra_cfg3,extra_cfg4])
