import contextlib
import os
import shutil
import subprocess
import time
import logging

import requests
from git import GitCommandError, Repo

logging.basicConfig(level=logging.INFO)
REBUILD_MARKER = '.rebuild'

REPO_URL = os.environ.get('REPO_URL')
REPO_BRANCH = os.environ.get('REPO_BRANCH', 'master')
BUILD_CMD = os.environ.get('BUILD_CMD')
ADD_PATH = '/add'
TIMEOUT = int(os.environ.get('TIMEOUT', '5'))
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_API = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'
TELEGRAM_CHATS = os.environ.get('TELEGRAM_CHATS', '').split(',')
PROJECT_NAME = os.environ.get('PROJECT_NAME', os.path.basename(REPO_URL))
HOST_DIR = os.environ['HOST_DIR']
LOCAL_PATH = os.path.join(HOST_DIR, 'repo', PROJECT_NAME)


def notify_telegram(msg):
    if TELEGRAM_TOKEN is None:
        return
    if TELEGRAM_CHATS == ['']:
        raise ValueError('Set TELEGRAM_CHATS to comma-separated list of chat ids. '
                         f'Find them out at {TELEGRAM_API}/getUpdates')
    for chat_id in TELEGRAM_CHATS:
        requests.post(f'{TELEGRAM_API}/sendMessage',
                      json={
                          "chat_id": chat_id,
                          "text": msg
                      }).raise_for_status()


def notify(msg):
    notify_telegram(msg)


@contextlib.contextmanager
def print_git_error():
    try:
        yield
    except GitCommandError as e:
        print('FAILED')
        print('stdout', e.stdout)
        print('stderr', e.stderr)
        raise


def build(repo: Repo):
    cmd = f'cd {LOCAL_PATH} && {BUILD_CMD}'
    print(f'Builing repo with {cmd}')
    notify(f'Building {PROJECT_NAME} from commit {repo.head.commit.hexsha[:8]} on branch {REPO_BRANCH}')
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    while True:
        poll = process.poll()
        output = process.stdout.readline()
        if output:
            print(output.strip().decode('utf8'))
        if poll is not None:
            break
    rc = process.poll()
    print('Done with code', rc)
    if rc == 0:
        notify(f'Build {PROJECT_NAME} [{repo.head.commit.hexsha[:8]}] succeeded')
    else:
        notify(f'Build {PROJECT_NAME} [{repo.head.commit.hexsha[:8]}] FAILED with code {rc}')


def check_new_commits(repo: Repo):
    """git remote update && git status """
    with print_git_error():
        repo.remote('origin').update()
    up_to_date = 'Your branch is up to date with' in repo.git.status(u='no')
    if not up_to_date:
        print('Changes detected in remote, pulling...')
        with print_git_error():
            repo.remote('origin').pull()
        build(repo)


def check_rebuild_marker(repo: Repo):
    if os.path.exists(REBUILD_MARKER):
        os.remove(REBUILD_MARKER)
        print('Rebuild triggered via marker')
        build(repo)


def run_loop(repo: Repo):
    while True:
        check_new_commits(repo)
        check_rebuild_marker(repo)
        time.sleep(TIMEOUT)


def copy_additional_files():
    if os.path.isdir(ADD_PATH):
        for path in os.listdir(ADD_PATH):
            src = os.path.join(ADD_PATH, path)
            trg = os.path.join(LOCAL_PATH, path)
            print(f'Copyind additional {src} to {trg}')
            shutil.copytree(src, trg, dirs_exist_ok=True)


def main():
    if not os.path.isdir(LOCAL_PATH) or len(os.listdir(LOCAL_PATH)) == 0:
        with print_git_error():
            print(f'Initializing new repo at {LOCAL_PATH}')
            repo = Repo.clone_from(REPO_URL, LOCAL_PATH)
            print(f'Checking out branch {REPO_BRANCH}')
            repo.git.checkout(REPO_BRANCH)
        copy_additional_files()
        build(repo)
    else:
        with print_git_error():
            print('Found existing repo')
            repo = Repo(LOCAL_PATH)
            if REPO_URL not in set(repo.remote('origin').urls):
                raise ValueError('Wrong origin url, please recreate container')
            print(f'Checking out branch {REPO_BRANCH}')
            repo.git.checkout(REPO_BRANCH)
    run_loop(repo)


if __name__ == '__main__':
    main()
