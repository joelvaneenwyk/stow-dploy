"""
A module that contains utility function mainly used for operations in the
missing from the pathlib module.
"""

from __future__ import print_function, unicode_literals

import os
import pathlib
import shutil
import stat
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Type, Union

from dploy.oschmod import get_mode, set_mode

StowPath = Union[os.PathLike[str], str, Path]
StowTreeIterable = Union[Dict[str, "StowTreeNode"], List["StowTreeNode"]]
StowTreeNode = Union[StowTreeIterable, StowPath]
StowTree = StowTreeNode
StowSources = Iterable[StowPath]
StowIgnorePatterns = Optional[Iterable[str]]


class Permission(int, Enum):
    """Permissions mapping for files and directories."""

    u_r = stat.S_IRUSR  # pylint: disable=invalid-name
    u_w = stat.S_IWUSR  # pylint: disable=invalid-name
    u_x = stat.S_IXUSR  # pylint: disable=invalid-name
    g_r = stat.S_IRGRP  # pylint: disable=invalid-name
    g_w = stat.S_IWGRP  # pylint: disable=invalid-name
    g_x = stat.S_IXGRP  # pylint: disable=invalid-name
    o_r = stat.S_IROTH  # pylint: disable=invalid-name
    o_w = stat.S_IWOTH  # pylint: disable=invalid-name
    o_x = stat.S_IXOTH  # pylint: disable=invalid-name


class Operation(Enum):
    """Operation to perform on a file or directory."""

    ADD = auto()
    REMOVE = auto()


Permission_Read = [Permission.u_r, Permission.g_r, Permission.o_r]
Permission_Write = [Permission.u_w, Permission.g_w, Permission.o_w]
Permission_Execute = [Permission.u_x, Permission.g_x, Permission.o_x]


def make_mode(init):
    # type: (Union[int, Iterable[str], None]) -> int
    """Make a mode integer from an initial value."""
    return Permissions.get_mode(init)


class _PermProperty(object):
    """Creates simple properties to get/set permissions."""

    def __init__(self, name):
        # type: (str) -> None
        self._name = name
        self.__doc__ = "Boolean for '{}' permission.".format(name)

    def __get__(self, obj, obj_type: Optional[Type["Permissions"]] = None):
        return self._name in obj

    def __set__(self, obj, value):
        # type: (Permissions, bool) -> None
        if value:
            obj.add(self._name)
        else:
            obj.remove(self._name)


class Permissions(object):
    """An abstraction for file system permissions.

    Permissions objects store information regarding the permissions
    on a resource. It supports Linux permissions, but is generic enough
    to manage permission information from almost any filesystem.

    Example:
        >>> from dploy.utils import Permissions
        >>> p = Permissions(user='rwx', group='rw-', other='r--')
        >>> print(p)
        rwxrw-r--
        >>> p.mode
        500
        >>> oct(p.mode)
        '0o764'
    """

    _LINUX_PERMS: list[tuple[str, int]] = [
        ("setuid", 2048),
        ("setguid", 1024),
        ("sticky", 512),
        ("u_r", 256),
        ("u_w", 128),
        ("u_x", 64),
        ("g_r", 32),
        ("g_w", 16),
        ("g_x", 8),
        ("o_r", 4),
        ("o_w", 2),
        ("o_x", 1),
    ]
    _LINUX_PERMS_NAMES: list[str] = [_name for _name, _mask in _LINUX_PERMS]

    def __init__(
        self,
        names=None,  # type: Optional[Iterable[str]]
        mode=None,  # type: Optional[int]
        user=None,  # type: Optional[str]
        group=None,  # type: Optional[str]
        other=None,  # type: Optional[str]
        sticky=None,  # type: Optional[bool]
        setuid=None,  # type: Optional[bool]
        setguid=None,  # type: Optional[bool]
    ):
        # type: (...) -> None
        """Create a new `Permissions` instance.

        Arguments:
            names (list, optional): A list of permissions.
            mode (int, optional): A mode integer.
            user (str, optional): A triplet of *user* permissions, e.g.
                ``"rwx"`` or ``"r--"``
            group (str, optional): A triplet of *group* permissions, e.g.
                ``"rwx"`` or ``"r--"``
            other (str, optional): A triplet of *other* permissions, e.g.
                ``"rwx"`` or ``"r--"``
            sticky (bool, optional): A boolean for the *sticky* bit.
            setuid (bool, optional): A boolean for the *setuid* bit.
            setguid (bool, optional): A boolean for the *setguid* bit.

        """
        if names is not None:
            self._perms = set(names)
        elif mode is not None:
            self._perms = {name for name, mask in self._LINUX_PERMS if mode & mask}
        else:
            perms = self._perms = set()
            perms.update("u_" + p for p in user or "" if p != "-")
            perms.update("g_" + p for p in group or "" if p != "-")
            perms.update("o_" + p for p in other or "" if p != "-")

        if sticky:
            self._perms.add("sticky")
        if setuid:
            self._perms.add("setuid")
        if setguid:
            self._perms.add("setguid")

    def __repr__(self):
        # type: () -> str
        if not self._perms.issubset(self._LINUX_PERMS_NAMES):
            _perms_str = ", ".join("'{}'".format(p) for p in sorted(self._perms))
            return "Permissions(names=[{}])".format(_perms_str)

        def _check(perm, name):
            # type: (str, str) -> str
            return name if perm in self._perms else ""

        user = "".join((_check("u_r", "r"), _check("u_w", "w"), _check("u_x", "x")))
        group = "".join((_check("g_r", "r"), _check("g_w", "w"), _check("g_x", "x")))
        other = "".join((_check("o_r", "r"), _check("o_w", "w"), _check("o_x", "x")))
        args = []
        _fmt = "user='{}', group='{}', other='{}'"
        basic = _fmt.format(user, group, other)
        args.append(basic)
        if self.sticky:
            args.append("sticky=True")
        if self.setuid:
            args.append("setuid=True")
        if self.setuid:
            args.append("setguid=True")
        return "Permissions({})".format(", ".join(args))

    def __str__(self):
        # type: () -> str
        return self.as_str()

    def __iter__(self) -> Iterable[str]:
        return iter(self._perms)

    def __contains__(self, permission):
        # type: (object) -> bool
        return permission in self._perms

    def __eq__(self, other):
        # type: (object) -> bool
        if isinstance(other, Permissions):
            names = other.dump()  # type: object
        else:
            names = other
        return self.dump() == names

    def __ne__(self, other):
        # type: (object) -> bool
        return not self.__eq__(other)

    @classmethod
    def parse(cls, ls):
        # type: (str) -> Permissions
        """Parse permissions in Linux notation."""
        user = ls[:3]
        group = ls[3:6]
        other = ls[6:9]
        return cls(user=user, group=group, other=other)

    @classmethod
    def load(cls, permissions):
        # type: (List[str]) -> Permissions
        """Load a serialized permissions object."""
        return cls(names=permissions)

    @classmethod
    def create(cls, init=None):
        # type: (Union[int, Iterable[str], None]) -> Permissions
        """Create a permissions object from an initial value.

        Arguments:
            init (int or list, optional): May be None to use `0o777`
                permissions, a mode integer, or a list of permission names.

        Returns:
            int: mode integer that may be used for instance by `os.makedir`.

        Example:
            >>> Permissions.create(None)
            Permissions(user='rwx', group='rwx', other='rwx')
            >>> Permissions.create(0o700)
            Permissions(user='rwx', group='', other='')
            >>> Permissions.create(['u_r', 'u_w', 'u_x'])
            Permissions(user='rwx', group='', other='')

        """
        if init is None:
            return cls(mode=0o777)
        if isinstance(init, cls):
            return init
        if isinstance(init, int):
            return cls(mode=init)
        if isinstance(init, list):
            return cls(names=init)
        raise ValueError("permissions is invalid")

    @classmethod
    def get_mode(cls, init):
        # type: (Union[int, Iterable[str], None]) -> int
        """Convert an initial value to a mode integer."""
        return cls.create(init).mode

    def copy(self):
        # type: () -> Permissions
        """Make a copy of this permissions object."""
        return Permissions(names=list(self._perms))

    def dump(self):
        # type: () -> List[str]
        """Get a list suitable for serialization."""
        return sorted(self._perms)

    def as_str(self):
        # type: () -> str
        """Get a Linux-style string representation of permissions."""
        perms = [c if name in self._perms else "-" for name, c in zip(self._LINUX_PERMS_NAMES[-9:], "rwxrwxrwx")]
        if "setuid" in self._perms:
            perms[2] = "s" if "u_x" in self._perms else "S"
        if "setguid" in self._perms:
            perms[5] = "s" if "g_x" in self._perms else "S"
        if "sticky" in self._perms:
            perms[8] = "t" if "o_x" in self._perms else "T"

        perm_str = "".join(perms)
        return perm_str

    @property
    def mode(self):
        # type: () -> int
        """`int`: mode integer."""
        mode = 0
        for name, mask in self._LINUX_PERMS:
            if name in self._perms:
                mode |= mask
        return mode

    @mode.setter
    def mode(self, mode):
        # type: (int) -> None
        self._perms = {name for name, mask in self._LINUX_PERMS if mode & mask}

    u_r = _PermProperty("u_r")
    u_w = _PermProperty("u_w")
    u_x = _PermProperty("u_x")

    g_r = _PermProperty("g_r")
    g_w = _PermProperty("g_w")
    g_x = _PermProperty("g_x")

    o_r = _PermProperty("o_r")
    o_w = _PermProperty("o_w")
    o_x = _PermProperty("o_x")

    sticky = _PermProperty("sticky")
    setuid = _PermProperty("setuid")
    setguid = _PermProperty("setguid")

    def add(self, *permissions):
        # type: (*str) -> None
        """Add permission(s).

        Arguments:
            *permissions (str): Permission name(s), such as ``'u_w'``
                or ``'u_x'``.

        """
        self._perms.update(permissions)

    def remove(self, *permissions):
        # type: (*str) -> None
        """Remove permission(s).

        Arguments:
            *permissions (str): Permission name(s), such as ``'u_w'``
                or ``'u_x'``.s

        """
        self._perms.difference_update(permissions)

    def check(self, *permissions):
        # type: (*str) -> bool
        """Check if one or more permissions are enabled.

        Arguments:
            *permissions (str): Permission name(s), such as ``'u_w'``
                or ``'u_x'``.

        Returns:
            bool: `True` if all given permissions are set.

        """
        return self._perms.issuperset(permissions)


def update_permissions(path: StowPath, operation: Operation, *permissions: Permission) -> None:
    """Add or remove permission(s) from a file or directory."""
    try:
        sys_path = Path(path).absolute()
        mode = get_mode(sys_path)
        for p in permissions:
            if operation == Operation.ADD:
                mode |= p
            else:
                mode &= ~p
        set_mode(sys_path, mode)
    except FileNotFoundError:
        pass


def get_directory_contents(directory: Path) -> list[Path]:
    """
    return a sorted list of the contents of a directory
    """
    contents: list[Path] = []

    for child in directory.iterdir():
        contents.append(child)

    return sorted(contents)


def rmtree(tree: StowPath):
    """
    a wrapper around shutil.rmtree to recursively delete a directory specified
    by a pathlib.Path object
    """
    shutil.rmtree(str(tree))


def is_same_file(file1: Path, file2: Path) -> bool:
    """
    test if two pathlib.Path() objects are the same file

    NOTE: python 3.5 supports pathlib.Path.samefile(file)
    NOTE: this can raise exception FileNotFoundError
    """
    return file1.resolve() == file2.resolve()


def is_same_files(files1: list[Path], files2: list[Path]) -> bool:
    """
    test if two collection of files are equivalent
    """
    files1_resolved = [f.resolve() for f in files1]
    files2_resolved = [f.resolve() for f in files2]
    return files1_resolved == files2_resolved


def get_absolute_path(file: StowPath) -> Path:
    """
    get the absolute path of a pathlib.Path() object
    """
    absolute_path = os.path.abspath(os.path.expanduser(str(file)))
    return pathlib.Path(absolute_path)


def get_relative_path(path: StowPath, start_at: StowPath) -> Path:
    """
    get the relative path of a pathlib.Path() object

    NOTE: python 3.4.5 & 3.5.2 support pathlib.Path.path =
    str(pathlib.Path)
    """
    try:
        relative_path = os.path.relpath(str(path), str(start_at))
    except ValueError:  # when a relative path does not exist
        return get_absolute_path(path)

    return pathlib.Path(relative_path)


def _get_access(path_item: StowPath) -> Permissions:
    return Permissions(mode=get_mode(path_item))


def is_file_readable(a_file: StowPath) -> bool:
    """check if a pathlib.Path() file is readable"""
    return _get_access(a_file).u_r


def is_file_writable(a_file: StowPath) -> bool:
    """
    check if a pathlib.Path() file is writable
    """
    return _get_access(a_file).u_w


def is_directory_readable(directory: StowPath) -> bool:
    """
    check if a pathlib.Path() directory is readable
    """
    return _get_access(directory).u_r


def is_directory_writable(directory: StowPath) -> bool:
    """
    check if a pathlib.Path() directory is writable
    """
    return _get_access(directory).u_w


def is_directory_executable(directory: StowPath) -> bool:
    """
    check if a pathlib.Path() directory is executable
    """
    return _get_access(directory).u_x


def readlink(path: StowPath, absolute_target: bool = False) -> Path:
    """
    get the target of a symbolic link passed as a pathlib.Path object and
    provide the option to return an absolute path even if the link target is
    relative.

    Note: we can't use pathlib.Path.resolve because it doesn't work for broken
    links and raises FileNotFoundError in (Python <3.5) and always returns a
    relative path

    """
    link_target = os.readlink(str(path))
    path_dir = os.path.dirname(str(path))
    if absolute_target:
        if not os.path.isabs(link_target):
            link_target = os.path.join(path_dir, link_target)
        return pathlib.Path(link_target)
    return pathlib.Path(link_target)
