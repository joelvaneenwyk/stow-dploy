"""
The variable __version__ is a string following the guidelines of semantic
versioning. The general guidelines are as follows

Given a version number MAJOR.MINOR.PATCH, increment the:

1. MAJOR version when you make incompatible API changes
2. MINOR version when you add functionality in a backwards-compatible manner
3. PATCH version when you make backwards-compatible bug fixes
4. Additional labels for pre-release and build metadata are available as
   extensions to the MAJOR.MINOR.PATCH format.
   e.g. 1.0.0-alpha+001, 1.0.0+20130313144700, 1.0.0-beta+exp.sha.5114f85
"""

import sys

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

# Single-sourcing the version from pyproject.toml
# https://packaging.python.org/guides/single-sourcing-package-version/

try:
    __version__ = metadata.version("dploy")
except metadata.PackageNotFoundError:
    __version__ = "unknown"
