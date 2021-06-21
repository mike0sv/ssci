import os
import shutil
import time

from git import Repo

from ..config import DeployConfig, SSCIConf
from ..deployment import Deployment
from ..log import logger
from .notifications.base import Notifier
from .utils import check_new_commits, print_git_error, run_detached, run_with_logs


def copy_additional_files(project: Deployment):
    if project.add_dir is not None and os.path.isdir(project.add_dir):
        for path in os.listdir(project.add_dir):
            src = os.path.join(project.add_dir, path)
            trg = os.path.join(project.local_path, path)
            logger.info(f"Copyind additional {src} to {trg} for {project.name}")
            if os.path.isdir(src):
                shutil.copytree(src, trg, dirs_exist_ok=True)
            else:
                shutil.copy(src, trg)


def build(repo: Deployment, notifier: Notifier):
    cmd = f"cd {repo.local_path} && ({repo.build_cmd})"
    logger.info(f"Builing repo with {cmd}")
    notifier.notify(
        f"Building {repo.name} from commit {repo.hexsha} "
        f"by {repo.repo.commit().author.name} on branch {repo.branch}"
    )

    if repo.build_detached:
        rc = run_detached(cmd, repo.build_detched_timeout)
    else:
        rc = run_with_logs(cmd)

    logger.info("Done with code %s", rc)
    if rc == 0:
        notifier.notify(f"Build {repo.name} [{repo.hexsha}] succeeded")
    else:
        notifier.notify(f"Build {repo.name} [{repo.hexsha}] FAILED with code {rc}")


def init_project(project: Deployment, notifier: Notifier, with_build=True):
    if (
        not os.path.isdir(project.local_path)
        or len(os.listdir(project.local_path)) == 0
    ):
        with print_git_error():
            logger.info(f"Initializing new {project.name} repo at {project.local_path}")
            repo = Repo.clone_from(project.url, project.local_path)
            logger.info(f"Checking out branch {project.branch}")
            repo.git.checkout(project.branch)
        copy_additional_files(project)
        if with_build:
            build(project, notifier)
    else:
        with print_git_error():
            logger.info(f"Found existing repo at {project.local_path}")
            repo = project.repo
            if project.url not in set(repo.remote("origin").urls):
                raise ValueError("Wrong origin url, please recreate container")
            logger.info(f"Checking out branch {project.branch}")
            repo.git.checkout(project.branch)


def check_rebuild_marker(config: DeployConfig):
    if os.path.exists(SSCIConf.REBUILD_MARKER):
        with open(SSCIConf.REBUILD_MARKER) as f:
            to_trigger_names = f.read().strip()
        os.remove(SSCIConf.REBUILD_MARKER)
        if to_trigger_names == "" or to_trigger_names == "*":
            to_trigger = config.projects
        else:
            to_trigger = [p for p in config.projects if p.name in to_trigger_names]
        logger.info(f"Rebuild triggered via marker {to_trigger_names} for {to_trigger}")
        for project in to_trigger:
            build(project, config.notifier)


def run_loop(config: DeployConfig):
    while True:
        try:
            for project in config.projects:
                check_new_commits(project, config.notifier)

            check_rebuild_marker(config)
        except Exception as e:
            print(f"Error: {e.__class__} {e.args}")
        time.sleep(SSCIConf.TIMEOUT)


def main(config: DeployConfig):
    for project in config.projects:
        init_project(project, config.notifier)

    run_loop(config)
