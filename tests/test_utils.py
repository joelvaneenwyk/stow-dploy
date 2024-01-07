"""
Tests for stow utils file
"""

# pylint: disable=missing-docstring
# disable lint errors for function names longer that 30 characters
# pylint: disable=invalid-name

import os
import pathlib

import pytest

from dploy import utils


def test_readlink_with_broken_absolute_target(dest):
    target = os.path.join("/", "source_only_files", "bbb")
    dest_path = os.path.join(dest, "bbb")
    os.symlink(target, dest_path)
    assert utils.readlink(dest_path) == pathlib.Path(target)
    assert utils.readlink(dest_path, absolute_target=True) == pathlib.Path(target)


def test_readlink_with_broken_relative_target(dest):
    target = os.path.join("..", "source_only_files", "bbb")
    dest_path = os.path.join(dest, "bbb")
    os.symlink(target, dest_path)
    assert utils.readlink(dest_path) == pathlib.Path(target)
    assert utils.readlink(dest_path, absolute_target=True) == pathlib.Path(dest) / pathlib.Path(target)


def test_readlink_with_relative_target(dest, source_a):
    # pylint: disable=unused-argument
    # disable lint errors for source_a since we don't use the variable but use
    # the fixture
    target = os.path.join("..", "source_a", "aaa")
    dest_path = os.path.join(dest, "bbb")
    os.symlink(target, dest_path)
    assert utils.readlink(dest_path) == pathlib.Path(target)
    assert utils.readlink(dest_path, absolute_target=True) == pathlib.Path(dest) / pathlib.Path(target)
    assert utils.readlink(dest_path, absolute_target=True).exists()


@pytest.mark.skip(reason="Not working yet.")
def test_readlink_with_absolute_target(dest, source_a):
    target = os.path.join(source_a, "aaa")
    dest_path = os.path.join(dest, "bbb")
    os.symlink(target, dest_path)
    assert utils.readlink(dest_path) == pathlib.Path(target)
    assert utils.readlink(dest_path, absolute_target=True) == pathlib.Path(target)
    assert utils.readlink(dest_path, absolute_target=True).exists()
    assert utils.readlink(dest_path).exists()
