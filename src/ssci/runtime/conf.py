import os

from decleverett import Config, Param


class Runtime(Config):
    HOST_DIR = Param(default=os.path.abspath("."))
    REPO_DIR = Param(default="repo")
