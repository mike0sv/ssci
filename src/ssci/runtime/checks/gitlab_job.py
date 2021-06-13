import time
from abc import ABC
from dataclasses import dataclass
from functools import cached_property

from gitlab import Gitlab
from gitlab.v4.objects import Project, ProjectPipeline
from ssci.deployment import Deployment
from ssci.log import logger
from ssci.runtime.checks.base import Check, CheckNotPassed


@dataclass
class PipelineFinished(Check, ABC):
    gitlab_host: str
    project_url: str
    private_token: str = None
    oauth_token: str = None
    start_timeout: float = 60
    pipeline_timeout: float = 60 * 60
    poll_timeout: float = 1

    def check(self, project: Deployment, commit: str):
        logger.info("Waiting for gitlab pipeline to succeed")
        pipeline = self.find_pipeline(commit)
        logger.info(f"Found gitlab pipeline {pipeline.web_url}")
        start = time.time()
        while time.time() - self.pipeline_timeout < start:
            pipeline: ProjectPipeline = self.gl_project.pipelines.get(pipeline.id)
            if pipeline.status == "success":
                logger.info("Gitlab pipeline succeeded")
                return True
            elif pipeline.status == "failed":
                raise CheckNotPassed(f"Gitlab pipeline failed {pipeline.web_url}")
            elif pipeline.status != "running":
                raise CheckNotPassed(
                    f"Unknown gitlab pipeline status {pipeline.web_url}"
                )
            time.sleep(self.poll_timeout)

    def find_pipeline(self, commit: str) -> ProjectPipeline:
        start = time.time()
        while time.time() - self.start_timeout < start:
            pipelines = [
                p for p in self.gl_project.pipelines.list() if p.sha.startswith(commit)
            ]
            if len(pipelines) > 0:
                return pipelines[0]
            time.sleep(self.poll_timeout)
        raise CheckNotPassed("Pipeline not started in time")

    @cached_property
    def gl_project(self) -> Project:
        gl_project = [
            p
            for p in self.gl.projects.list()
            if p.http_url_to_repo.startswith(self.project_url)
        ]
        if len(gl_project) == 0:
            raise CheckNotPassed("No projects found")
        return gl_project[0]

    @cached_property
    def gl(self) -> Gitlab:
        return Gitlab(self.gitlab_host, self.private_token, self.oauth_token)
