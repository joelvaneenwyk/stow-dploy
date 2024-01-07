"""
A module that contains utility function mainly used for operations in the
missing from the pathlib module.
"""

import os
import pathlib
import shutil
import stat
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import fs
import fs.osfs
import fs.permissions
from fs.errors import MissingInfoNamespace

from dploy.oschmod import get_mode, set_mode

StowPath = Union[os.PathLike[str], str, Path]
StowTreeIterable = Union[Dict[str, "StowTreeNode"], List["StowTreeNode"]]
StowTreeNode = Union[StowTreeIterable, StowPath]
StowTree = StowTreeNode
StowSources = Iterable[StowPath]
StowIgnorePatterns = Optional[Iterable[str]]


def _get_fs(path: StowPath) -> tuple[fs.osfs.OSFS, str]:
    """
    get a filesystem object from a path
    """
    try:
        input_path_item = Path(path).resolve(strict=True)
        root = fs.path.normpath(input_path_item.anchor)
        rel = fs.path.normpath(str(input_path_item))
        fs_mount = fs.osfs.OSFS(root, create=True, create_mode=0o777, expand_vars=True)
        fs_path = fs.path.normpath(rel.replace(root, "")).replace("\\", "/")
    except IOError as io_error:
        raise FileNotFoundError(f"Invalid file or directory: {path}") from io_error
    return fs_mount, fs_path


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


Permissions = Iterable[Permission]
Permission_Read = [Permission.u_r, Permission.g_r, Permission.o_r]
Permission_Write = [Permission.u_w, Permission.g_w, Permission.o_w]
Permission_Execute = [Permission.u_x, Permission.g_x, Permission.o_x]


def update_permissions(
    path: StowPath, operation: Operation, *permissions: Permission
) -> None:
    """Add or remove permission(s) from a file or directory."""
    try:
        os_file_system, input_path_item = _get_fs(path)
        mode = get_mode(os_file_system.getsyspath(input_path_item))
        for p in permissions:
            if operation == Operation.ADD:
                mode |= p
            else:
                mode &= ~p
        set_mode(os_file_system.getsyspath(input_path_item), mode)
    except MissingInfoNamespace:
        pass
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


def _get_access(path_item: StowPath) -> fs.permissions.Permissions:
    mode = get_mode(path_item)
    return fs.permissions.Permissions(mode=mode)


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
