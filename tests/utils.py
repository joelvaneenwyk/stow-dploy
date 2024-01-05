"""
Contains utilities used during testing
"""

import os
import shutil
import stat
from pathlib import Path


def remove_tree(tree):
    """
    reset the permission of a file and directory tree and remove it
    """
    os.chmod(tree, 0o777)
    shutil.rmtree(tree)


def remove_file(file_name):
    """
    reset the permission of a file and remove it
    """
    os.chmod(file_name, 0o777)
    os.remove(file_name)


def create_file(file_name):
    """
    create an file
    """
    return open(file_name, "w", encoding="utf8").close()


def create_directory(directory_name):
    """
    create an directory
    """
    os.makedirs(directory_name)


class ChangeDirectory:
    # pylint: disable=too-few-public-methods
    """
    Context manager for changing the current working directory
    """

    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def create_tree(tree):
    """
    create an file and directory tree
    """
    for branch in tree:
        if isinstance(branch, str):
            create_file(branch)

        elif isinstance(branch, dict):
            for directory, file_objs in branch.items():
                create_directory(directory)

                with ChangeDirectory(directory):
                    create_tree(file_objs)


def remove_read_permission(path):
    """
    change users permissions to a path to write only
    """
    mode = os.stat(path)[stat.ST_MODE]
    os.chmod(path, mode & ~stat.S_IRUSR & ~stat.S_IRGRP & ~stat.S_IROTH)


def add_read_permission(path):
    """
    change users permissions to a path to write only
    """
    mode = os.stat(path)[stat.ST_MODE]
    os.chmod(path, mode | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def remove_write_permission(path):
    """
    change users permissions to a path to read only
    """
    mode = os.stat(path)[stat.ST_MODE]
    os.chmod(path, mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)


def remove_execute_permission(path):
    """
    change users permissions to a path to read only
    """
    mode = os.stat(path)[stat.ST_MODE]
    os.chmod(path, mode & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH)


def restore_tree_permissions(top_directory: os.PathLike) -> None:
    """Reset users's permissions on a directory tree."""
    top_directory_path = Path(top_directory)
    if not top_directory_path.is_dir():
        raise NotADirectoryError(f"Invalid directory: {top_directory}")

    add_user_permissions(top_directory_path)

    for current_dir, dirs, files in os.walk(top_directory_path):
        for file_name in dirs + files:
            add_user_permissions(Path(current_dir).joinpath(file_name))


def add_user_permissions(path: os.PathLike) -> None:
    """Restore owner's file/dir permissions."""
    if not os.path.exists(path) and not os.path.islink(path):
        raise FileNotFoundError(f"Invalid file or directory: {path}")

    wanted = stat.S_IREAD | stat.S_IWRITE
    if os.path.isdir(path):
        wanted |= stat.S_IEXEC

    mode = stat.S_IMODE(os.lstat(path).st_mode)
    if mode & wanted != wanted and not os.path.islink(path):
        os.chmod(path, mode | wanted)
