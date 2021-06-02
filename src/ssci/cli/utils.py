import click

from ssci.config import DeployConfig


def get_project(name: str, index=False):
    cfg = DeployConfig.load()
    indexes = [i for i, p in enumerate(cfg.projects) if p.name == name]
    if len(indexes) == 0:
        click.echo(f'No projects with name {name} found. To list projects, use ssci show')
        raise click.Abort()
    pi = indexes[0]
    if index:
        return pi
    else:
        return cfg.projects[pi]
