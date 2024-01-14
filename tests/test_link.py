"""
Tests for the link sub command
"""
# pylint: disable=missing-docstring
# disable lint errors for function names longer that 30 characters
# pylint: disable=invalid-name

import os

import pytest

import dploy
from dploy import error, permissions
import dploy.stowcmd

SUBCMD = dploy.stowcmd.DploySubCommand.LINK


def test_link_with_directory_as_source(source_a: str, dest: str):
    dploy.link(source_a, os.path.join(dest, "source_a_link"))
    assert os.path.islink(os.path.join(dest, "source_a_link"))


def test_link_with_file_as_source(file_a: str, dest: str):
    dploy.link(file_a, os.path.join(dest, "file_a"))
    assert os.path.islink(os.path.join(dest, "file_a"))


def test_link_with_non_existant_source(dest: str):
    non_existant_source = "source_a"
    message = error.as_match(error.NoSuchFileOrDirectory(subcmd=SUBCMD, file=non_existant_source))
    with pytest.raises(error.NoSuchFileOrDirectory, match=message):
        dploy.link(non_existant_source, os.path.join(dest, "source_a_link"))


def test_link_with_non_existant_dest(source_a: str):
    non_existant_dest = "dest"
    message = error.as_match(error.NoSuchFileOrDirectory(subcmd=SUBCMD, file=non_existant_dest))
    with pytest.raises(error.NoSuchFileOrDirectory, match=message):
        dploy.link(source_a, os.path.join(non_existant_dest, "source_a_link"))


def test_link_with_read_only_dest(file_a: str, dest: str):
    dest_file = os.path.join(dest, "file_a_link")
    permissions.remove_write_permission(dest)
    message = error.as_match(error.InsufficientPermissions(subcmd=SUBCMD, file=dest_file))
    with pytest.raises(error.InsufficientPermissions, match=message):
        dploy.link(file_a, dest_file)


def test_link_with_write_only_source(file_a: str, dest: str):
    dest_file = os.path.join(dest, "file_a_link")
    permissions.remove_read_permission(file_a)
    message = error.as_match(error.InsufficientPermissions(subcmd=SUBCMD, file=file_a))
    with pytest.raises(error.InsufficientPermissions, match=message):
        dploy.link(file_a, dest_file)


def test_link_with_conflicting_broken_link_at_dest(file_a: str, dest: str):
    dest_file = os.path.join(dest, "file_a_link")
    os.symlink("non_existant_source", dest_file)
    message = error.as_match(error.ConflictsWithExistingLink(subcmd=SUBCMD, source=file_a, dest=dest_file))
    with pytest.raises(error.ConflictsWithExistingLink, match=message):
        dploy.link(file_a, dest_file)
