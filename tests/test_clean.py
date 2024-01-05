"""
Tests for the link sub command
"""
# pylint: disable=missing-docstring
# disable lint errors for function names longer that 30 characters
# pylint: disable=invalid-name

import os

import dploy

SUBCMD = "clean"


def test_clean_with_simple_scenario(source_only_files, dest):
    broken = os.path.join("..", "source_only_files", "bbb")
    dest_path = os.path.join(dest, "bbb")
    os.symlink(broken, dest_path)
    assert os.readlink(dest_path) == broken
    dploy.clean([source_only_files], dest)
    assert not os.path.exists(dest_path)


def test_clean_after_stow_removing_invalid_link_from_source(source_a, dest):
    dploy.stow([source_a], dest)
    broken = os.path.join("..", "source_a", "bbb")
    dest_path = os.path.join(dest, "bbb")
    os.symlink(broken, dest_path)
    assert os.readlink(dest_path) == broken
    dploy.clean([source_a], dest)
    assert not os.path.exists(dest_path)
    assert os.readlink(os.path.join(dest, "aaa")) == os.path.join(
        "..", "source_a", "aaa"
    )


def test_clean_after_stow_not_removing_invalid_link_from_other_source(source_a, dest):
    dploy.stow([source_a], dest)
    broken = os.path.join("..", "source_b", "bbb")
    dest_path = os.path.join(dest, "bbb")
    os.symlink(broken, dest_path)
    assert os.readlink(dest_path) == broken
    dploy.clean([source_a], dest)
    assert os.readlink(dest_path) == broken
