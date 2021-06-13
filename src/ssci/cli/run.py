from .main import cli
from .utils import with_project
from ..config import DeployConfig
from ..deployment import Deployment
from ..runtime.main import main, build as build_proj


@cli.command()
def run():
    main(DeployConfig.load())


@cli.command()
@with_project(include_cfg=True)
def build(cfg, project: Deployment):
    build_proj(project, cfg.notifier)
