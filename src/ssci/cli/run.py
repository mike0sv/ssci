from ..config import DeployConfig
from ..deployment import Deployment
from ..runtime.main import build as build_proj
from ..runtime.main import main
from .main import cli
from .utils import with_project


@cli.command()
def run():
    """Run ssci runtime (not in container)"""
    main(DeployConfig.load())


@cli.command()
@with_project(include_cfg=True)
def build(cfg, project: Deployment):
    """Run project build (not in container)"""
    build_proj(project, cfg.notifier)
