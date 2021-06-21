from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyjackson.decorators import type_field
from ssci.abc import Configurable

if TYPE_CHECKING:
    from ssci.deployment import Deployment


@dataclass
class CheckNotPassed(Exception):
    reason: str


@type_field("type")
class Check(ABC, Configurable):
    KNOWN = {"gitlab": "ssci.runtime.checks.gitlab_job.PipelineFinished"}

    @abstractmethod
    def check(self, project: "Deployment", commit: str):
        """"""
