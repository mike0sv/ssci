import contextlib
import os
from pprint import pprint
from typing import Type

import click
import yaml
from pyjackson import deserialize
from pyjackson._typing_utils import is_union
from pyjackson.utils import get_class_fields, resolve_subtype

from ..abc import Configurable
from ..config import DeployConfig, SSCIConf
from ..deployment import Deployment
from ..runtime.checks.base import Check
from ..runtime.notifications.base import Notifier
from .main import cli
from .utils import get_project


@contextlib.contextmanager
def load_save_config():
    try:
        with open(SSCIConf.CONFIG_PATH) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        data = {}
    yield data
    with open(SSCIConf.CONFIG_PATH, "w") as f:
        yaml.safe_dump(data, f)


@cli.command()
def config():
    """Print current ssci config"""
    cfg = DeployConfig.load()
    pprint(cfg)


@cli.command()
@click.argument("option")
@click.argument("value")
def set(option, value):
    """Set config option to new value"""
    with load_save_config() as data:
        get = data.get("ssci", {})
        get[option] = value
        data["ssci"] = get


@cli.command()
def new():
    """Initiate new ssci deployment in interactive mode"""
    cfg = DeployConfig.load()

    repo_url = click.prompt("Remote git repo url?")
    name = None
    while name is None or any(d.name == name for d in cfg.projects):
        name = click.prompt("Name of deployment?", default=os.path.basename(repo_url))
        if any(d.name == name for d in cfg.projects):
            click.echo("Deployment with that name already exists")

    branch = click.prompt("Branch to deploy?", default="main")
    dind = click.confirm("Do you need dind?", default=True)
    build_cmd = click.prompt(
        "Enter build command:",
        default="docker-compose up --build -d --remove-orphans" if dind else "",
    )
    add_dir = click.prompt("Dir with additional files:", default="")
    deploy = Deployment(
        repo_url=repo_url,
        build_cmd=build_cmd,
        branch=branch,
        project_name=name,
        add_dir=add_dir if add_dir else None,
        dind=dind,
    )

    cfg.projects.append(deploy)
    cfg.save()


@cli.command()
@click.argument("project")
def remove(project):
    """Remove deployment project"""
    cfg = DeployConfig.load()
    index = get_project(project, index=True)
    cfg.projects.pop(index)
    click.echo(f"Removed project {project}")
    cfg.save()


@cli.command()
@click.argument("project")
@click.argument("branch")
def switch(project, branch):
    """Switch project branch"""
    cfg = DeployConfig.load()
    p = get_project(project)
    click.echo(f"Switched project {project} to branch {branch}")
    p.branch = branch
    cfg.save()


@cli.command()
@click.argument("project", default="")
def show(project):
    """Print one or all projects configuration"""
    cfg = DeployConfig.load()

    if project == "":
        click.echo("------Projects--------")
        click.echo("\n".join("* " + p.project_name for p in cfg.projects))
        click.echo("----------------------")
    else:
        p = cfg.get_project(project)
        if p is None:
            click.echo(f"No such project {project}")
        else:
            click.echo(f"Project {project}")
            click.echo(p)


def create_configurable(cls: Type[Configurable], kind):
    kind = cls.KNOWN.get(kind, kind)
    args = {"type": kind}
    clazz = resolve_subtype(cls, args)
    for field in get_class_fields(clazz):
        try:
            cast = field.type.__args__[0] if is_union(field.type) else field.type
            args[field.name] = cast(
                click.prompt(f"{field.name} value?", default=field.default)
            )
        except ValueError:
            raise NotImplementedError(f"Not yet implemented for type {field.type}")
    return deserialize(args, cls)


@cli.command()
@click.argument("kind", default="telegram")
def notification(kind):
    """Add new notification destination"""
    cfg = DeployConfig.load()

    cfg.notifications.append(create_configurable(Notifier, kind))
    cfg.save()


@cli.command()
@click.argument("project")
@click.argument("kind")
def addcheck(project, kind):
    """Add new check to project"""
    cfg = DeployConfig.load()
    cfg.get_project(project).checks.append(create_configurable(Check, kind))
    cfg.save()
