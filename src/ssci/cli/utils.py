from functools import wraps

import click
from ssci.config import DeployConfig


def with_project(required=False, include_cfg=False, allow_one=True):
    def outer(f):
        @click.argument("project", default="" if allow_one else None)
        @wraps(f)
        def inner(project, *args, **kwargs):
            cfg = DeployConfig.load()
            if project == "" and allow_one and len(cfg.projects) == 1:
                p = cfg.projects[0]
            else:
                p = get_project(project, cfg=cfg)
            if required and p is None:
                return
            if include_cfg:
                res = f(cfg, p, *args, **kwargs)
            else:
                res = f(p, *args, **kwargs)
            return res

        return inner

    return outer


def get_project(name: str, index=False, cfg: DeployConfig = None):
    cfg = cfg or DeployConfig.load()
    indexes = [i for i, p in enumerate(cfg.projects) if p.name == name]
    if len(indexes) == 0:
        click.echo(
            f"No projects with name {name} found. To list projects, use ssci show"
        )
        raise click.Abort()
    pi = indexes[0]
    if index:
        return pi
    else:
        return cfg.projects[pi]
