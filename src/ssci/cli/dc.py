import contextlib
import os
import tempfile

import click
import docker

from .main import cli
from .utils import get_project
from ..config import DeployConfig, SSCIConf
from ..cookie import render
from ..runtime.utils import run_with_logs


@contextlib.contextmanager
def docker_compose(path:str=None):
    path = path or SSCIConf.COMPOSE_FILE
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(render(DeployConfig.load()))
    yield path


@cli.command()
@click.argument('project', default='')
def rebuild(project):
    if project == '':
        project = '*'
    else:
        get_project(project)
    click.echo(f"Triggering rebuild for projects {project}")
    with docker_compose() as path:
        run_with_logs(f"docker-compose -f {path} exec ssci ash -c 'echo \"{project}\" > {SSCIConf.REBUILD_MARKER}'")


@cli.group()
def dc():
    pass


@dc.command()
def show():
    click.echo(render(DeployConfig.load()))


@dc.command()
def start():
    with docker_compose()as path:
        run_with_logs(f"docker-compose -f {path} up -d")


@dc.command()
def stop():
    with docker_compose() as path:
        run_with_logs(f"docker-compose -f {path} stop")

@dc.command()
def restart():
    with docker_compose() as path:
        run_with_logs(f"docker-compose -f {path} restart")

@dc.command()
@click.argument('command', default='ash')
def exec(command):
    with docker_compose() as path:
        run_with_logs(f"docker-compose -f {path} exec ssci {command}")