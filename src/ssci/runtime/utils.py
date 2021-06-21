import contextlib
import subprocess
import time

from git import GitCommandError
from ssci.deployment import Deployment
from ssci.log import logger
from ssci.runtime.notifications.base import Notifier


@contextlib.contextmanager
def print_git_error(reraise=True):
    try:
        yield
    except GitCommandError as e:
        logger.info("FAILED")
        logger.info("stdout %s", e.stdout)
        logger.info("stderr %s", e.stderr)
        if reraise:
            raise


def check_new_commits(deployment: Deployment, notifier: Notifier):
    """git remote update && git status"""
    with print_git_error():
        deployment.repo.remote("origin").update()
    up_to_date = "Your branch is up to date with" in deployment.repo.git.status(u="no")
    if not up_to_date:
        logger.info(f"Changes detected in remote for {deployment.name}, pulling...")
        with print_git_error():
            deployment.repo.remote("origin").pull()
        from ssci.runtime.main import build  # FIXME

        build(deployment, notifier)


def run_with_logs(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    while True:
        poll = process.poll()
        output = process.stdout.readline()
        if output:
            logger.info(output.strip().decode("utf8"))
        if poll is not None:
            break
    return process.poll()


def run_detached(cmd, timeout):
    logger.info(f"Waiting {timeout} seconds...")
    process = subprocess.Popen(cmd, shell=True)
    start = time.time()
    while time.time() - timeout < start:
        time.sleep(1)
        rc = process.poll()
    return rc or 0
