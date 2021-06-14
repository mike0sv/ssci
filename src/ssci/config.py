import os
from functools import lru_cache
from typing import List

try:
    from functools import cached_property
except ImportError:  # python < 3.8 compatibility
    from cached_property import cached_property

import yaml
from decleverett import Config, Param
from decleverett.yaml import add_yaml_source
from pyjackson import deserialize, serialize
from pyjackson.decorators import make_string
from ssci.deployment import Deployment
from ssci.runtime.notifications.base import MultiNotifier, Notifier


class SSCIConf(Config):
    namespace = "ssci"
    CONFIG_PATH = Param(default="ssci.yaml")
    COMPOSE_FILE = Param(default="docker-compose.yml")
    TIMEOUT = Param(parser=float, default="5.")
    REBUILD_MARKER = Param(default=".rebuild")
    SERVICE_NAME = Param(default=os.path.basename(os.path.abspath(".")))
    DEPLOY = Param(default="", parser=dict)
    KEYS_DIR = Param(default="keys")


YamlEnv = add_yaml_source(SSCIConf.CONFIG_PATH)


@make_string
class DeployConfig:
    def __init__(
        self, projects: List[Deployment] = None, notifications: List[Notifier] = None
    ):
        self.projects = projects or []
        self.notifications = notifications or []

    def get_project(self, name):
        projects = [p for p in self.projects if p.name == name]
        if len(projects) == 0:
            return
        return projects[0]

    def save(self, path: str = None):
        path = path or SSCIConf.CONFIG_PATH
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            data = {"ssci": {}}

        data["ssci"]["deploy"] = serialize(self)
        with open(path, "w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    @lru_cache
    def load(cls) -> "DeployConfig":
        return deserialize(SSCIConf.DEPLOY, cls)

    @cached_property
    def notifier(self):
        return MultiNotifier(self.notifications)
