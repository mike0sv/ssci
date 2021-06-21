import os
import shutil

import click

from ..config import DeployConfig
from ..runtime.conf import Runtime
from ..runtime.main import copy_additional_files, init_project
from .main import cli
from .utils import get_project


@cli.command()
@click.argument("project", default="")
def pull(project):
    """Pull one or all projects"""
    cfg = DeployConfig.load()
    if project == "":
        click.echo("Going to pull all projects")
        to_pull = cfg.projects
    else:
        click.echo(f"Going to pull project {project}")
        to_pull = [p for p in cfg.projects if p.name == project]
    if len(to_pull) == 0:
        click.echo("No projects found")

    for p in to_pull:
        init_project(p, cfg.notifier, False)


@cli.command()
@click.argument("project", default="")
def readd(project):
    """Re-run copying addtional files for one or all projects
    Warning - does not check if project is currently running
    """
    cfg = DeployConfig.load()
    # FIXME check if stopped
    if project == "":
        click.echo("Readding all projects")
        projects = cfg.projects
    else:
        click.echo(f"Readding project {project}")
        projects = [get_project(project)]

    for p in projects:
        copy_additional_files(p)


@cli.command()
@click.argument("project", default="")
def clean(project):
    """Remove one or all projects repos
    Warning - does not check if project is currently running
    """
    # FIXME check if stopped
    if project == "":
        click.echo("Cleaning all projects")
        shutil.rmtree(Runtime.REPO_DIR, ignore_errors=True)
    else:
        click.echo(f"Cleaning project {project}")
        get_project(project)
        shutil.rmtree(os.path.join(Runtime.REPO_DIR, project), ignore_errors=True)
