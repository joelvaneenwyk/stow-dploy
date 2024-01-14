"""
The logic and workings behind the stow and unstow sub-commands
"""

import pathlib
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum, auto
from typing import Final, Protocol

from dploy import actions, error, ignore
from dploy.utils import StowIgnorePatterns, StowPath, StowSources


class DploySubCommand(Enum):
    """Subcommands allowed for use with 'dploy' tool."""

    STOW = auto()
    CLEAN = auto()
    LINK = auto()
    UNSTOW = auto()


class BaseSubCommandProtocol(Protocol):
    """Subcommand protocol for 'dploy' package."""

    subcmd: DploySubCommand

    def _check_for_other_actions(self):
        """Abstract method for examine the existing action to see if more actions
        need to be added or if some actions need to be removed.
        """

    @abstractmethod
    def _is_valid_input(self, sources: StowSources, dest: pathlib.Path) -> bool:
        """Abstract method to check if the input to a sub-command is valid."""

    @abstractmethod
    def _collect_actions(self, source: pathlib.Path, dest: pathlib.Path):
        """Abstract method that collects the actions required to complete a sub-command."""


class AbstractBaseSubCommand(ABC, BaseSubCommandProtocol):  # pylint: disable=too-few-public-methods
    """
    An abstract class to unify shared functionality in stow commands
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        subcmd: DploySubCommand,
        sources: StowSources,
        dest: StowPath,
        is_silent: bool,
        is_dry_run: bool,
        ignore_patterns: StowIgnorePatterns,
    ):
        self.subcmd = subcmd

        self.actions: Final[actions.Actions] = actions.Actions(is_silent, is_dry_run)
        self.errors: Final[error.Errors] = error.Errors(is_silent)

        self._ignore_patterns: Final[StowIgnorePatterns] = ignore_patterns

        self.is_silent: Final[bool] = is_silent
        self.is_dry_run: Final[bool] = is_dry_run

        self.dest_input: Final[pathlib.Path] = pathlib.Path(dest)

        self.ignore_sources: dict[pathlib.Path, ignore.Ignore] = {}
        self._sources: list[pathlib.Path] = []

        source_inputs = [pathlib.Path(source) for source in sources]
        if self._is_valid_input(source_inputs, self.dest_input):
            for source in source_inputs:
                self._add_source(source)

        for source in self._sources:
            self._collect_actions(source, self.dest_input)

        self._check_for_other_actions()
        self._execute_actions()

    def should_ignore(self, source):
        """
        Checks if a source should be ignored
        """
        self._add_source(source)
        return source not in self.ignore_sources or self.ignore_sources[source].should_ignore(source)

    def _add_source(self, source):
        """
        Checks if a source should be ignored
        """
        if source not in self._sources:
            if source not in self.ignore_sources:
                self.ignore_sources[source] = ignore.Ignore(self._ignore_patterns, source)

            if self.ignore_sources[source].should_ignore(source):
                self.ignore_sources[source].ignore(source)

            self._sources.append(source)
        return source

    def _execute_actions(self):
        """
        Either executes collected actions by a sub command or raises collected
        exceptions.
        """
        self.errors.handle()
        self.actions.execute()


class Input(ABC):  # pylint: disable=too-few-public-methods
    """
    Input validator abstract base class
    """

    def __init__(self, errors, subcmd):
        self.errors = errors
        self.subcmd = subcmd

    def is_valid(self, sources, dest):
        """
        Checks if the passes in source and dest are valid
        """
        is_input_valid = True
        if not self._is_there_duplicate_sources(sources) and self._is_valid_dest(dest):
            for source in sources:
                if not self._is_valid_source(source):
                    is_input_valid = False
        else:
            is_input_valid = False

        return is_input_valid

    def _is_there_duplicate_sources(self, sources):
        """
        Checks sources to see if there are any duplicates
        """

        is_there_duplicates = False

        tally = defaultdict(int)
        for source in sources:
            tally[source] += 1

        for source, count in tally.items():
            if count > 1:
                is_there_duplicates = True
                self.errors.add(error.DuplicateSource(self.subcmd, source))

        return is_there_duplicates

    @abstractmethod
    def _is_valid_dest(self, dest: pathlib.Path):
        """
        Abstract method to check if the dest input to a sub-command is valid
        """
        pass

    @abstractmethod
    def _is_valid_source(self, source: StowPath):
        """
        Abstract method to check if the source input to a sub-command is valid
        """
        pass
