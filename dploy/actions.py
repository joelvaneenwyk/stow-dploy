"""
This module contains the actions that are combined to perform dploy's sub
commands
"""

from collections import defaultdict
from pathlib import Path
from typing import Callable, Final, Protocol, TypeGuard, TypeVar, runtime_checkable

from dploy import error, utils
from dploy.main import DploySubCommand


class AbstractBaseAction(Protocol):  # pylint: disable=too-few-public-methods
    """An abstract base class that define the interface for actions."""

    execute: Callable[[], None]
    """Function that executes the logic of each concrete action.    """


@runtime_checkable
class ActionSourceProtocol(Protocol):
    """Action needing a source."""

    source: Path


@runtime_checkable
class ActionDestinationProtocol(Protocol):
    """Action that requires destination."""

    dest: Path


@runtime_checkable
class ActionTargetProtocol(Protocol):
    """Action that needs a target path."""

    target: Path


@runtime_checkable
class ActionSourceDestProtocol(ActionSourceProtocol, ActionDestinationProtocol, Protocol):
    """Action that requires destination."""

    dest: Path


T = TypeVar("T", bound=AbstractBaseAction)  # Declare type variable "U"


def is_action_with_source_and_destination(action: AbstractBaseAction) -> TypeGuard[ActionSourceDestProtocol]:
    """Gets an action"""
    return isinstance(action, ActionSourceDestProtocol)


class Actions:
    """Collects and executes actions."""

    def __init__(self, is_silent: bool, is_dry_run: bool):
        self.actions: list[AbstractBaseAction] = []
        self.is_silent: Final[bool] = is_silent
        self.is_dry_run: Final[bool] = is_dry_run

    def add(self, action: AbstractBaseAction):
        """Adds an action"""
        self.actions.append(action)

    def execute(self) -> None:
        """Prints and executes actions"""
        for action in self.actions:
            if not self.is_silent:
                print(action)
            if not self.is_dry_run:
                action.execute()

    def get_unlink_actions(self) -> list["UnLink"]:
        """get the current Unlink() actions from the self.actions"""
        return [a for a in self.actions if isinstance(a, UnLink)]

    def get_unlink_target_parents(self) -> list[Path]:
        """Get list of the parents for the current Unlink() actions from
        self.actions
        """
        unlink_actions = self.get_unlink_actions()
        # sort for deterministic output
        return sorted({a.target.parent for a in unlink_actions})

    def get_unlink_targets(self) -> list[Path]:
        """Get list of the targets for the current Unlink() actions from
        self.actions
        """
        unlink_actions = self.get_unlink_actions()
        return [a.target for a in unlink_actions]

    def get_duplicates(self) -> list[list[int]]:
        """return a tuple containing tuples with the following structure
        (link destination, [indices of duplicates])
        """
        tally: dict[Path, list[int]] = defaultdict(list)
        for index, action in enumerate(self.actions):
            if isinstance(action, SymbolicLink):
                destination = action.dest
                tally[destination].append(index)
        # sort for deterministic output
        return sorted([indices for _, indices in tally.items() if len(indices) > 1])


class SymbolicLink(AbstractBaseAction, ActionSourceProtocol, ActionDestinationProtocol):
    # pylint: disable=too-few-public-methods
    """Action to create a symbolic link relative to the source of the link"""

    def __init__(self, subcmd: DploySubCommand, source: Path, dest: Path):
        super().__init__()
        self.source = source
        self.source_relative = utils.get_relative_path(source, dest.parent)
        self.subcmd = subcmd
        self.dest = dest

    def execute(self):
        try:
            self.dest.symlink_to(self.source_relative)
        except PermissionError as permission_error:
            raise error.InsufficientPermissionsToSubcmdTo(self.subcmd, self.dest) from permission_error

    def __repr__(self):
        return "dploy {subcmd}: link {dest} => {source}".format(
            subcmd=self.subcmd, dest=self.dest, source=self.source_relative
        )


class AlreadyLinked(AbstractBaseAction, ActionSourceProtocol, ActionDestinationProtocol):
    # pylint: disable=too-few-public-methods
    """Action to used to print an already linked message"""

    def __init__(self, subcmd: DploySubCommand, source: Path, dest: Path):
        super().__init__()
        self.source = source
        self.source_relative = utils.get_relative_path(source, dest.parent)
        self.dest = dest
        self.subcmd = subcmd

    def execute(self):
        pass

    def __repr__(self):
        return "dploy {subcmd}: already linked {dest} => {source}".format(
            subcmd=self.subcmd, source=self.source_relative, dest=self.dest
        )


class AlreadyUnlinked(AbstractBaseAction, ActionSourceProtocol, ActionDestinationProtocol):
    # pylint: disable=too-few-public-methods
    """Action to used to print an already unlinked message"""

    def __init__(self, subcmd: DploySubCommand, source: Path, dest: Path):
        super().__init__()
        self.source = source
        self.source_relative = utils.get_relative_path(source, dest.parent)
        self.dest = dest
        self.subcmd = subcmd

    def execute(self):
        pass

    def __repr__(self):
        return "dploy {subcmd}: already unlinked {dest} => {source}".format(
            subcmd=self.subcmd, source=self.source_relative, dest=self.dest
        )


class UnLink(AbstractBaseAction, ActionTargetProtocol):
    # pylint: disable=too-few-public-methods
    """Action to unlink a symbolic link"""

    def __init__(self, subcmd: DploySubCommand, target: Path):
        super().__init__()
        self.target = target
        self.subcmd = subcmd

    def execute(self):
        if not self.target.is_symlink():
            # pylint: disable=line-too-long
            raise RuntimeError(
                "dploy detected and aborted an attempt to unlink a non-symlink {target} this is a bug and should be reported".format(
                    target=self.target
                )
            )
        self.target.unlink()

    def __repr__(self):
        return "dploy {subcmd}: unlink {target} => {source}".format(
            subcmd=self.subcmd, target=self.target, source=utils.readlink(self.target)
        )


class MakeDirectory(AbstractBaseAction, ActionTargetProtocol):
    # pylint: disable=too-few-public-methods
    """Action to create a directory"""

    def __init__(self, subcmd, target):
        super().__init__()
        self.target = target
        self.subcmd = subcmd

    def execute(self):
        self.target.mkdir()

    def __repr__(self):
        return "dploy {subcmd}: make directory {target}".format(target=self.target, subcmd=self.subcmd)


class RemoveDirectory(AbstractBaseAction, ActionTargetProtocol):
    # pylint: disable=too-few-public-methods
    """Action to remove a directory"""

    def __init__(self, subcmd: DploySubCommand, target: Path):
        super().__init__()
        self.target = target
        self.subcmd = subcmd

    def execute(self):
        self.target.rmdir()

    def __repr__(self):
        msg = "dploy {subcmd}: remove directory {target}"
        return msg.format(target=self.target, subcmd=self.subcmd)
