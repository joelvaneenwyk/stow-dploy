"""
Contains utilities used during testing
"""

import os
import shutil
from pathlib import Path

from dploy.oschmod import set_mode
from dploy.utils import (
    Operation,
    Permission,
    Permission_Execute,
    Permission_Read,
    Permission_Write,
    StowPath,
    StowTree,
    update_permissions,
)


def remove_tree(tree: StowPath):
    """reset the permission of a file and directory tree and remove it"""
    set_mode(tree, 0o777)
    shutil.rmtree(tree)


def remove_file(file_name: StowPath):
    """reset the permission of a file and remove it"""
    set_mode(file_name, 0o777)
    os.remove(file_name)


def create_file(file_name: StowPath) -> str:
    """create an file"""
    open(file_name, "w", encoding="utf8").close()
    return str(file_name)


def create_directory(directory_name: StowPath):
    """create an directory"""
    os.makedirs(directory_name)


class ChangeDirectory:
    # pylint: disable=too-few-public-methods
    """Context manager for changing the current working directory"""

    def __init__(self, new_path: StowPath):
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def create_tree(tree: StowTree) -> None:
    """
    create an file and directory tree
    """
    try:
        if isinstance(tree, str) or isinstance(tree, Path):
            create_file(tree)
        elif isinstance(tree, list):
            for branch in tree:
                create_tree(branch)
        elif isinstance(tree, dict):
            for directory, file_objs in tree.items():
                create_directory(directory)

                with ChangeDirectory(directory):
                    create_tree(file_objs)
    except TypeError:
        pass


def remove_read_permission(path: StowPath) -> None:
    """change users permissions to a path to write only"""
    update_permissions(path, Operation.remove, *Permission_Read)


def remove_write_permission(path: StowPath) -> None:
    """Change users permissions to a path to read only"""
    update_permissions(path, Operation.remove, *Permission_Write)


def remove_execute_permission(path: StowPath) -> None:
    """Change users permissions to a path to read only."""
    update_permissions(path, Operation.remove, *Permission_Execute)


def add_read_permission(path: StowPath) -> None:
    """Change users permissions to a path to write only"""
    update_permissions(path, Operation.add, *Permission_Read)


def add_execute_permission(path: StowPath) -> None:
    """Change users permissions to a path to read only"""
    update_permissions(path, Operation.add, *Permission_Execute)


def restore_tree_permissions(top_directory: StowPath) -> None:
    """Reset users's permissions on a directory tree."""
    top_directory_path = Path(top_directory)
    if not top_directory_path.is_dir():
        raise NotADirectoryError(f"Invalid directory: {top_directory}")

    add_user_permissions(top_directory_path)

    for current_dir, dirs, files in os.walk(top_directory_path):
        for file_name in dirs + files:
            add_user_permissions(Path(current_dir).joinpath(file_name))


def add_user_permissions(path: StowPath) -> None:
    """Restore owner's file/dir permissions."""
    if not os.path.exists(path) and not os.path.islink(path):
        raise FileNotFoundError(f"Invalid file or directory: {path}")

    update_permissions(path, Operation.add, *[Permission.u_r, Permission.u_w])
    if os.path.isdir(path):
        update_permissions(path, Operation.add, *[Permission.u_x])
