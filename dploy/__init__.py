"""
dploy script is an attempt at creating a clone of GNU stow that will work on
Windows as well as *nix
"""


import sys
assert sys.version_info >= (3, 3), "Requires Python 3.3 or Greater"
import os
import pathlib
import dploy.command

class Stow():
    """
    todo
    """
    def __init__(self, source, dest):
        source_input = pathlib.Path(source)
        dest_input = pathlib.Path(dest)

        if not source_input.exists():
            msg = "dploy stow: can not stow '{file}': No such directory"
            print(msg.format(file=source_input))
            sys.exit(1)

        if not dest_input.exists():
            msg = "dploy stow: can not stow into '{file}': No such directory"
            print(msg.format(file=dest_input))
            sys.exit(1)

        source_absolute = _get_absolute_path(source_input)
        dest_absolute = _get_absolute_path(dest_input)


        self.commands = []
        self.abort = False

        self.basic(source_absolute, dest_absolute)
        self.execute_commands()


    def execute_commands(self):
        """
        todo
        """
        if self.abort:
            sys.exit(1)
        else:
            for cmd in self.commands:
                # print(cmd)
                cmd.execute()


    def unfold(self, dest, source):
        """
        todo
        """
        sources = []

        for source_child in source.iterdir():
            sources.append(source_child)

        self.commands.append(dploy.command.UnLink(dest))
        self.commands.append(dploy.command.MakeDirectory(dest))
        self.collect_commands(sources, dest)


    def basic(self, source, dest):
        """
        todo
        """
        assert source.is_dir()
        assert source.is_absolute()
        assert dest.is_absolute()

        src_files = []

        for src_file in source.iterdir():
            src_files.append(src_file)

        self.collect_commands(src_files, dest)


    def collect_commands(self, sources, dest):
        """
        todo
        """
        for source in sources:
            dest_path = dest / pathlib.Path(source.name)
            source_relative = _get_relative_path(source,
                                                 dest_path.parent)
            if dest_path.exists():
                if _is_same_file(dest_path, source):
                    self.commands.append(
                        dploy.command.SymbolicLinkExists(source_relative,
                                                         dest_path))
                elif dest_path.is_dir() and source.is_dir:
                    if dest_path.is_symlink():
                        self.unfold(dest_path, source)
                    self.basic(source, dest_path)
                else:
                    msg = "dploy stow: can not stow '{file}': Conflicts with existing file"
                    print(msg.format(file=dest_path))
                    self.abort = True
            elif not dest_path.parent.exists():
                msg = "dploy stow: can not stow into '{dest}': No such directory"
                print(msg.format(dest=dest_path.parent))
                self.abort = True
            else:
                self.commands.append(
                    dploy.command.SymbolicLink(source_relative, dest_path))



def stow(source, dest):
    """
    sub command stow
    """

    Stow(source, dest)


def link(source, dest):
    """
    sub command link
    """
    source_input = pathlib.Path(source)
    dest_input = pathlib.Path(dest)

    if not source_input.exists():
        msg = "dploy link: can not link '{file}': No such directory"
        print(msg.format(file=source_input))
        sys.exit(1)

    source_absolute = _get_absolute_path(source_input)
    dest_absolute = _get_absolute_path(dest_input)

    _link_absolute_paths(source_absolute, dest_absolute)


def _link_absolute_paths(source, dest):
    """
    todo
    """
    assert source.is_absolute()
    assert dest.is_absolute()
    assert source.exists()

    src_file_relative = _get_relative_path(source,
                                           dest.parent)
    try:
        dest.symlink_to(src_file_relative)
        msg = "Link: {dest} => {source}"
        print(msg.format(source=src_file_relative, dest=dest))

    except FileExistsError:
        if _is_same_file(dest, source):
            msg = "Link: Already Linked {dest} => {source}"
            print(msg.format(source=src_file_relative, dest=dest))

        else:
            msg = "Abort: {file} Already Exists"
            print(msg.format(file=dest))
            sys.exit(1)

    except FileNotFoundError:
        msg = "Abort: {dest} Not Found"
        print(msg.format(dest=dest))
        sys.exit(1)


def _is_same_file(file1, file2):
    """
    todo

    NOTE: python 3.5 supports pathlib.Path.samefile(file)
    """
    return file1.resolve() == file2.resolve()

def _get_absolute_path(file):
    """
    todo
    """
    absolute_path = os.path.abspath(os.path.expanduser(file.__str__()))
    return pathlib.Path(absolute_path)

def _get_relative_path(path, start_at):
    """
    NOTE: python 3.4.5 & 3.5.2 support pathlib.Path.path = pathlib.Path.__str__()
    """
    return pathlib.Path(os.path.relpath(path.__str__(), start_at.__str__()))
