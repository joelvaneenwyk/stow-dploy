"""
Tests for the stow sub command
"""
# pylint: disable=missing-docstring
# disable lint errors for function names longer that 30 characters
# pylint: disable=invalid-name
# pylint: disable=line-too-long

import os

import pytest

import dploy
from dploy import error, permissions
import dploy.stowcmd

SUBCMD = dploy.stowcmd.DploySubCommand.UNSTOW


def test_unstow_with_basic_scenario(source_a, dest):
    dploy.stow([source_a], dest)
    dploy.unstow([source_a], dest)
    assert not os.path.exists(os.path.join(dest, "aaa"))


def test_unstow_with_basic_scenario_does_not_delete_dest_directory(source_a, dest):
    dploy.stow([source_a], dest)
    dploy.unstow([source_a], dest)
    assert os.path.exists(dest)


def test_unstow_with_a_broken_link_dest(source_a, dest):
    conflicting_link = os.path.join(dest, "aaa")
    source_file = os.path.join(source_a, "aaa")
    os.symlink("non_existant_source", os.path.join(dest, "aaa"))

    message = error.as_match(error.ConflictsWithExistingLink(subcmd=SUBCMD, source=source_file, dest=conflicting_link))

    with pytest.raises(error.ConflictsWithExistingLink, match=message):
        dploy.unstow([source_a], dest)


def test_unstow_with_broken_link_in_dest(source_a, dest):
    os.makedirs(os.path.join(dest, "aaa"))
    dploy.stow([source_a], dest)
    os.symlink(
        os.path.join(source_a, "non_existant_source"),
        os.path.join(dest, "aaa", "non_existant_source"),
    )
    dploy.unstow([source_a], dest)


def test_unstow_with_non_existant_source(dest):
    source = "source"
    message = error.as_match(error.NoSuchDirectory(subcmd=SUBCMD, file=source))
    with pytest.raises(error.NoSuchDirectory, match=message):
        dploy.unstow([source], dest)


def test_unstow_with_duplicate_source(source_a, dest):
    dploy.stow([source_a], dest)
    message = error.as_match(error.DuplicateSource(subcmd=SUBCMD, file=source_a))
    with pytest.raises(error.DuplicateSource, match=message):
        dploy.unstow([source_a, source_a], dest)


def test_unstow_with_non_existant_dest(source_a):
    dest = "dest"
    message = error.as_match(error.NoSuchDirectoryToSubcmdInto(subcmd=SUBCMD, file=dest))
    with pytest.raises(error.NoSuchDirectoryToSubcmdInto, match=message):
        dploy.unstow([source_a], dest)


def test_unstow_with_file_as_source(file_a, dest):
    message = error.as_match(error.NoSuchDirectory(subcmd=SUBCMD, file=file_a))
    with pytest.raises(error.NoSuchDirectory, match=message):
        dploy.unstow([file_a], dest)


def test_unstow_with_file_as_dest(source_a, file_a):
    message = error.as_match(error.NoSuchDirectoryToSubcmdInto(subcmd=SUBCMD, file=file_a))
    with pytest.raises(error.NoSuchDirectoryToSubcmdInto, match=message):
        dploy.unstow([source_a], file_a)


def test_unstow_with_file_as_source_and_dest(file_a, file_b):
    message = error.as_match(error.NoSuchDirectoryToSubcmdInto(subcmd=SUBCMD, file=file_b))
    with pytest.raises(error.NoSuchDirectoryToSubcmdInto, match=message):
        dploy.unstow([file_a], file_b)


def test_unstow_with_read_only_dest(source_a, dest):
    dploy.stow([source_a], dest)
    permissions.remove_write_permission(dest)
    message = error.as_match(error.InsufficientPermissionsToSubcmdTo(subcmd=SUBCMD, file=dest))
    with pytest.raises(error.InsufficientPermissionsToSubcmdTo, match=message):
        dploy.unstow([source_a], dest)


def test_unstow_with_read_only_dest_file(source_a, dest):
    dploy.stow([source_a], dest)
    permissions.remove_write_permission(os.path.join(dest, "aaa"))
    dploy.unstow([source_a], dest)


def test_unstow_with_write_only_source(source_a, dest):
    dploy.stow([source_a], dest)
    permissions.remove_read_permission(source_a)
    message = error.as_match(error.InsufficientPermissionsToSubcmdFrom(subcmd=SUBCMD, file=source_a))
    with pytest.raises(error.InsufficientPermissionsToSubcmdFrom, match=message):
        dploy.unstow([source_a], dest)

    permissions.add_read_permission(source_a)


def test_unstow_with_dest_with_no_execute_permissions(source_a, dest):
    dploy.stow([source_a], dest)
    permissions.remove_execute_permission(dest)
    message = error.as_match(error.InsufficientPermissionsToSubcmdTo(subcmd=SUBCMD, file=dest))
    with pytest.raises(error.InsufficientPermissionsToSubcmdTo, match=message):
        dploy.unstow([source_a], dest)


def test_unstow_with_dest_dir_with_no_execute_permissions(source_a, source_b, dest):
    dest_dir = os.path.join(dest, "aaa")
    dploy.stow([source_a, source_b], dest)
    permissions.remove_execute_permission(os.path.join(dest, "aaa"))
    message = error.as_match(error.InsufficientPermissionsToSubcmdTo(subcmd=SUBCMD, file=dest_dir))
    with pytest.raises(error.InsufficientPermissionsToSubcmdTo, match=message):
        dploy.unstow([source_a, source_b], dest)


def test_unstow_with_write_only_source_file(source_a, dest):
    dploy.stow([source_a], dest)
    permissions.remove_read_permission(os.path.join(source_a, "aaa", "aaa"))
    dploy.unstow([source_a], dest)


def test_unstow_with_write_only_dest_file(source_a, dest):
    dploy.stow([source_a], dest)
    permissions.remove_read_permission(os.path.join(dest, "aaa"))
    dploy.unstow([source_a], dest)


def test_unstow_with_same_directory_used_as_source_and_dest(source_a):
    message = error.as_match(error.SourceIsSameAsDest(subcmd=SUBCMD, file=source_a))
    with pytest.raises(error.SourceIsSameAsDest, match=message):
        dploy.unstow([source_a], source_a)


def test_unstow_with_same_simple_directory_used_as_source_and_dest(source_only_files):
    message = error.as_match(error.SourceIsSameAsDest(subcmd=SUBCMD, file=source_only_files))
    with pytest.raises(error.SourceIsSameAsDest, match=message):
        dploy.unstow([source_only_files], source_only_files)


def test_unstow_folding_basic(source_a, source_b, dest):
    dploy.stow([source_a, source_b], dest)
    dploy.unstow([source_b], dest)
    assert os.path.islink(os.path.join(dest, "aaa"))


def test_unstow_folding_with_multiple_sources(source_a, source_b, source_d, dest):
    dploy.stow([source_a, source_b, source_d], dest)
    dploy.unstow([source_b, source_d], dest)
    assert os.path.islink(os.path.join(dest, "aaa"))


def test_unstow_folding_with_stray_symlink_in_unfolded_dest_dir(source_a, source_b, source_d, dest):
    """
    Given a dest directory with stowed packages that share a unfolded directory,
    that also contains a stray link along with the links created by stowing.

    When the stowed packages are unstowed

    Then the folded directory remains with the single stray symlink
    """
    stray_path = os.path.join(dest, "aaa", "ggg")
    dploy.stow([source_a, source_b], dest)
    dploy.link(os.path.join(source_d, "aaa", "ggg"), stray_path)
    dploy.unstow([source_a, source_b], dest)
    assert os.path.islink(stray_path)


def test_unstow_folding_with_multiple_stowed_sources(source_a, source_b, source_d, dest):
    dploy.stow([source_a, source_b, source_d], dest)
    dploy.unstow([source_b], dest)
    assert not os.path.islink(os.path.join(dest, "aaa"))


def test_unstow_folding_with_multiple_sources_all_unstowed(source_a, source_b, dest):
    dploy.stow([source_a, source_b], dest, is_silent=False)
    dploy.unstow([source_a, source_b], dest, is_silent=False)
    assert not os.path.exists(os.path.join(dest, "aaa"))


def test_unstow_folding_with_existing_file_in_dest(source_a, source_b, dest):
    os.makedirs(os.path.join(dest, "aaa"))
    a_file = os.path.join(dest, "aaa", "a_file")
    permissions.create_file(a_file)
    dploy.stow([source_a, source_b], dest)
    dploy.unstow([source_a], dest)
    assert os.path.exists(a_file)


@pytest.mark.skip(reason="Not working yet.")
def test_unstow_folding_with_multiple_sources_with_execute_permission_unset(source_a, source_b, dest):
    dploy.stow([source_a, source_b], dest)
    permissions.remove_execute_permission(source_b)
    dest_dir = os.path.join(dest, "aaa", "ddd")
    message = error.as_match(error.PermissionDenied(subcmd=SUBCMD, file=dest_dir))
    with pytest.raises(error.PermissionDenied, match=message):
        dploy.unstow([source_a], dest)
