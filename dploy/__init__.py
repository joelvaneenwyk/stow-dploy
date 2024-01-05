"""
dploy script is an attempt at creating a clone of GNU stow that will work on
Windows as well as *nix
"""

import sys

from dploy import linkcmd, stowcmd
from dploy.utils import StowIgnorePatterns, StowPath, StowSources

assert sys.version_info >= (3, 3), "Requires Python 3.3 or Greater"


def stow(
    sources: StowSources,
    dest: StowPath,
    is_silent: bool = True,
    is_dry_run: bool = False,
    ignore_patterns: StowIgnorePatterns = None,
):
    """
    sub command stow
    """
    stowcmd.Stow(sources, dest, is_silent, is_dry_run, ignore_patterns)


def unstow(
    sources: StowSources,
    dest: StowPath,
    is_silent: bool = True,
    is_dry_run: bool = False,
    ignore_patterns: StowIgnorePatterns = None,
):
    """
    sub command unstow
    """
    stowcmd.UnStow(sources, dest, is_silent, is_dry_run, ignore_patterns)


def clean(
    sources: StowPath,
    dest: StowPath,
    is_silent: bool = True,
    is_dry_run: bool = False,
    ignore_patterns: StowIgnorePatterns = None,
):
    """
    sub command clean
    """
    stowcmd.Clean(sources, dest, is_silent, is_dry_run, ignore_patterns)


def link(
    source: StowPath,
    dest: StowPath,
    is_silent: bool = True,
    is_dry_run: bool = False,
    ignore_patterns: StowIgnorePatterns = None,
):
    """
    sub command link
    """
    linkcmd.Link(source, dest, is_silent, is_dry_run, ignore_patterns)
