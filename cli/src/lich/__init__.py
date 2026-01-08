"""
Lich Toolkit - AI-Ready Full-Stack Project Generator.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("lich")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"
