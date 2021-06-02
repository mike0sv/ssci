import os
from dataclasses import dataclass
from functools import cached_property

from git import Repo

from ssci.runtime.conf import Runtime


@dataclass
class Deployment:
    repo_url: str
    build_cmd: str
    branch: str = 'main'
    project_name: str = None
    add_dir: str = None
    dind: bool = False

    @property
    def add_abs(self):
        return os.path.abspath(self.add_dir)

    @property
    def name(self):
        return self.project_name or os.path.basename(self.repo_url)

    @property
    def local_path(self):
        return os.path.join(Runtime.HOST_DIR, Runtime.REPO_DIR, self.project_name)

    @cached_property
    def repo(self) -> Repo:
        return Repo(self.local_path)

    @property
    def hexsha(self):
        return self.repo.head.commit.hexsha[:8]
