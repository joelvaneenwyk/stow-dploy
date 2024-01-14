"""
Tests for the CLI interface
"""
# pylint: disable=missing-docstring
# disable lint errors for function names longer that 30 characters
# pylint: disable=invalid-name

import os
import re

import pytest

import dploy.cli


def test_cli_with_stow_with_simple_scenario(source_only_files: str, dest: str, capsys: pytest.CaptureFixture[str]):
    args = ["stow", source_only_files, dest]
    assert dploy.cli.run(args) == 0
    assert os.readlink(os.path.join(dest, "aaa")) == os.path.join("..", "source_only_files", "aaa")
    out, _ = capsys.readouterr()
    d = os.path.join(dest, "aaa")
    s = os.path.relpath(os.path.join(source_only_files, "aaa"), dest)
    assert out == "dploy stow: link {dest} => {source}\n".format(source=s, dest=d)


def test_cli_unstow_with_basic_scenario(source_a: str, dest: str, capsys: pytest.CaptureFixture[str]):
    args_stow = ["stow", source_a, dest]
    assert dploy.cli.run(args_stow) == 0
    assert os.readlink(os.path.join(dest, "aaa")) == os.path.join("..", "source_a", "aaa")

    args_unstow = ["unstow", source_a, dest]
    assert dploy.cli.run(args_unstow) == 0
    assert not os.path.exists(os.path.join(dest, "aaa"))

    out, _ = capsys.readouterr()
    src_dir = os.path.relpath(os.path.join(source_a, "aaa"), dest)
    dest_dir = os.path.join(dest, "aaa")
    expected_output = (
        "dploy stow: link {dest_dir} => {src_dir}\n" "dploy unstow: unlink {dest_dir} => {src_dir}\n".format(
            src_dir=src_dir, dest_dir=dest_dir
        )
    )
    assert out == (expected_output)


def test_cli_with_link_directory(source_a: str, dest: str, capsys: pytest.CaptureFixture[str]):
    args = ["link", source_a, os.path.join(dest, "source_a_link")]
    assert dploy.cli.run(args) == 0
    assert os.path.islink(os.path.join(dest, "source_a_link"))
    output, _ = capsys.readouterr()
    expected_output_unformatted = "dploy link: link {dest} => {source}\n"
    expected_output = expected_output_unformatted.format(
        source=os.path.relpath(source_a, dest), dest=os.path.join(dest, "source_a_link")
    )
    assert output == expected_output


def test_cli_with_dry_run_option_with_stow_with_simple_scenario(
    source_only_files: str, dest: str, capsys: pytest.CaptureFixture[str]
):
    args = ["--dry-run", "stow", source_only_files, dest]
    assert dploy.cli.run(args) == 0
    assert not os.path.exists(os.path.join(dest, "aaa"))
    out, _ = capsys.readouterr()
    d = os.path.join(dest, "aaa")
    s = os.path.relpath(os.path.join(source_only_files, "aaa"), dest)
    assert out == "dploy stow: link {dest} => {source}\n".format(source=s, dest=d)


def test_cli_with_silent_option_with_stow_with_simple_scenario(
    source_only_files: str, dest: str, capsys: pytest.CaptureFixture[str]
):
    args = ["--silent", "stow", source_only_files, dest]
    assert dploy.cli.run(args) == 0
    assert os.readlink(os.path.join(dest, "aaa")) == os.path.join("..", "source_only_files", "aaa")
    out, _ = capsys.readouterr()
    assert out == ""


def test_cli_with_version_option(capsys: pytest.CaptureFixture[str]):
    args = ["--version"]
    with pytest.raises(SystemExit):
        assert dploy.cli.run(args) == 0
        out, _ = capsys.readouterr()
        assert re.match(r"dploy \d+.\d+\.\d+(-\w+)?\n", out) is not None
