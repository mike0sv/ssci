import os
import subprocess
from urllib.parse import urlparse

import click

from .main import cli
from .utils import with_project
from ..config import DeployConfig, SSCIConf
from ..deployment import Deployment


@cli.group()
def github():
    pass


def key_path(project, public=False):
    return os.path.join(SSCIConf.KEYS_DIR, f'deploy_{project.name}' + ('.pub' if public else ''))


def host_name(project):
    return f'ssci_deploy_{project.name}'


@github.command()
@with_project(True, True)
def gen(cfg: DeployConfig, project: Deployment):
    path = key_path(project)
    if os.path.exists(path):
        click.echo(f'Key already exists at {path}')
        click.Abort()
        return
    os.makedirs(SSCIConf.KEYS_DIR, exist_ok=True)
    print(subprocess.check_output(f'ssh-keygen -t rsa -b 4096 -f {path} -N ""', shell=True).decode('utf8'))
    project.key_file = path
    cfg.save()
    click.echo(f'Run "ssci github patch {project.name}" to add ssh config and add this as deploy key')
    with open(key_path(project, True)) as f:
        click.echo(f.read())


@github.command()
@with_project(True)
def pub(project: Deployment):
    path = key_path(project, True)
    if not os.path.exists(path):
        click.echo(f'No public key found, generate it with "ssci github gen {project.name}"')
        click.Abort()
        return
    with open(path)as f:
        click.echo(f"Public key for {project.name}")
        click.echo(f.read())


@github.command()
@with_project(True)
@click.option('-c', '--config_path', default=os.path.expanduser('~/.ssh/config'))
def patch(project: Deployment, config_path: str):
    conf = f"""
Host {host_name(project)}
    HostName {urlparse(project.repo_url).netloc}
    IdentityFile {key_path(project)}
    """
    try:
        with open(config_path, 'r') as f:
            if conf in f.read():
                click.echo("Your config already patched")
                return
        with open(config_path, 'a') as f:
            f.write(conf)
        click.echo('Success')
    except (OSError, FileNotFoundError):
        click.echo(f"Could not patch {config_path}, please do it manually")
        click.echo("-" * 10)
        click.echo(conf)
        click.echo("-" * 10)
