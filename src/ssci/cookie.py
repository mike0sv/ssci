import os
from pathlib import Path

from jinja2 import Template
from ssci.config import DeployConfig, SSCIConf
from ssci.runtime.conf import Runtime


def render(cfg: DeployConfig):
    with open(Path(__file__).parent / "templates" / "docker-compose.yml") as f:
        template = Template(f.read())

    return template.render(
        projects=cfg.projects,
        host_dir=Runtime.HOST_DIR,
        service_name=SSCIConf.SERVICE_NAME,
        dind=any(p.dind for p in cfg.projects),
        repo=os.path.abspath(Runtime.REPO_DIR),
        abs_conf=os.path.abspath(SSCIConf.CONFIG_PATH),
        conf=SSCIConf.CONFIG_PATH,
        keys=SSCIConf.KEYS_DIR,
    )
