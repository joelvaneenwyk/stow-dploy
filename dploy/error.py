"""
All the exceptions and their messages used by the program
"""
import re
import sys

ERROR_HEAD = "dploy {subcmd}: can not {subcmd} "


def as_match(error):
    """
    Returns a regex match for the error
    """
    return re.escape(str(error))


class Errors:
    """
    A class that collects and executes action objects
    """

    def __init__(self, is_silent):
        self.exceptions = []
        self.is_silent = is_silent

    def add(self, error):
        """
        Adds an error
        """
        self.exceptions.append(error)

    def handle(self):
        """
        Prints and handles errors
        """
        if len(self.exceptions) > 0:
            if not self.is_silent:
                for exception in self.exceptions:
                    print(exception, file=sys.stderr)
            raise self.exceptions[0]


class DployError(Exception):
    """Base error exception for package."""
    pass


class SourceIsSameAsDest(DployError):
    """A source argument is the same as the dest argument"""
    def __init__(self, subcmd, file):
        self.msg = (
            ERROR_HEAD + "'{file}': A source argument is the same as the dest argument"
        )
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = ValueError(self.msg)

    def __str__(self):
        return self.msg


class ConflictsWithAnotherSource(DployError):
    """the following: Conflicts with other source files"""
    def __init__(self, subcmd, files):
        self.msg = ERROR_HEAD + "the following: Conflicts with other source {files}"
        files_list = "\n    " + "\n    ".join(files)
        self.msg = self.msg.format(subcmd=subcmd, files=files_list)
        # self.exception = ValueError(self.msg)

    def __str__(self):
        return self.msg


class ConflictsWithExistingFile(DployError):
    """Source Conflicts with existing file at destination"""
    def __init__(self, subcmd, source, dest):
        self.msg = ERROR_HEAD + "'{source}': Conflicts with existing file '{dest}'"
        self.msg = self.msg.format(subcmd=subcmd, source=source, dest=dest)
        # self.exception = ValueError(self.msg)

    def __str__(self):
        return self.msg


class ConflictsWithExistingLink(DployError):
    """Source Conflicts with existing symlink at destination"""
    def __init__(self, subcmd, source, dest):
        self.msg = ERROR_HEAD + "'{source}': Conflicts with existing symlink '{dest}'"
        self.msg = self.msg.format(subcmd=subcmd, source=source, dest=dest)
        # self.exception = ValueError(self.msg)

    def __str__(self):
        return self.msg


class InsufficientPermissions(DployError):
    """Insufficient permissions"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': Insufficient permissions"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = PermissionError(self.msg)

    def __str__(self):
        return self.msg


class NoSuchDirectory(DployError):
    """No such directory"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': No such directory"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = NotADirectoryError(self.msg)

    def __str__(self):
        return self.msg


class PermissionDenied(DployError):
    """Permission denied"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': Permission denied"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = PermissionError(self.msg)

    def __str__(self):
        return self.msg


class InsufficientPermissionsToSubcmdFrom(DployError):
    """from Insufficient permissions"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "from '{file}': Insufficient permissions"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = PermissionError(self.msg)

    def __str__(self):
        return self.msg


class NoSuchDirectoryToSubcmdInto(DployError):
    """into No such directory"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "into '{file}': No such directory"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = NotADirectoryError(self.msg)

    def __str__(self):
        return self.msg


class InsufficientPermissionsToSubcmdTo(DployError):
    """to Insufficient permissions"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "to '{file}': Insufficient permissions"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = PermissionError(self.msg)

    def __str__(self):
        return self.msg


class NoSuchFileOrDirectory(DployError):
    """No such file or directory"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': No such file or directory"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = FileNotFoundError(self.msg)

    def __str__(self):
        return self.msg


class DuplicateSource(DployError):
    """Duplicate source argument"""
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': Duplicate source argument"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        # self.exception = ValueError(self.msg)

    def __str__(self):
        return self.msg
