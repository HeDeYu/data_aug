"""Top-level package for data_aug."""

from . import data_package  # noqa: F401
from ._version import get_versions
from .data_package import *  # noqa: F401, F403

__author__ = """Deyu He"""
__email__ = "18565286660@163.com"
__version__ = get_versions()["version"]
del get_versions
