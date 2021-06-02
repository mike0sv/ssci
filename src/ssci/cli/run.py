from .main import cli
from ..config import DeployConfig
from ..runtime.main import main


@cli.command()
def run():
    main(DeployConfig.load())
