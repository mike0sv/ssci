import os
from dataclasses import dataclass
from functools import cached_property
from typing import List

from git import Remote, Repo
from ssci.runtime.checks.base import Check
from ssci.runtime.conf import Runtime


@dataclass
class Deployment:
    repo_url: str
    build_cmd: str
    branch: str = "main"
    project_name: str = None
    add_dir: str = None
    dind: bool = False
    checks: List[Check] = tuple()
    key_file: str = None
    build_detached: bool = False
    build_detched_timeout: float = 10

    @property
    def url(self):
        if self.key_file is not None:
            from ssci.cli.github import host_name

            owner, name = os.path.split(self.repo_url)
            _, owner = os.path.split(owner)
            return f"git@{host_name(self)}:{owner}/{name}"
        return self.repo_url

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

    def run_checks(self):
        remote: Remote = self.repo.remote("origin")
        remote.update()
        commit = remote.refs[0].commit.hexsha
        for check in self.checks:
            check.check(self, commit)
