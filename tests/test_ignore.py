"""
Tests for the ignore feature
"""
# pylint: disable=missing-docstring
# disable lint errors for function names longer that 30 characters
# pylint: disable=invalid-name

import os

import dploy

SUBCMD = "stow"


def test_ignore_by_ignoring_everything(source_a: str, source_c: str, dest: str):
    dploy.stow([source_a, source_c], dest, ignore_patterns=["*"])
    assert not os.path.exists(os.path.join(dest, "aaa"))


def test_ignore_by_ignoring_only_subdirectory(source_a: str, source_c: str, dest: str):
    dploy.stow([source_a, source_c], dest, ignore_patterns=["aaa"])
    assert not os.path.exists(os.path.join(dest, "aaa"))


def test_ignore_by_ignoring_everything_(source_a: str, source_c: str, dest: str):
    dploy.stow([source_a, source_c], dest, ignore_patterns=["source_*/aaa"])
    assert not os.path.exists(os.path.join(dest, "aaa"))


def test_ignore_by_ignoring_everything__(source_a: str, source_c: str, dest: str):
    dploy.stow([source_a, source_c], dest, ignore_patterns=["*/aaa"])
    assert not os.path.exists(os.path.join(dest, "aaa"))


def test_ignore_file_by_ignoring_everything__(source_a, source_c, file_dploystowignore, dest):
    ignore_patterns = ["*/aaa"]
    with open(file_dploystowignore, "w", encoding="utf8") as file:
        file.write("\n".join(ignore_patterns))
    dploy.stow([source_a, source_c], dest)
    assert not os.path.exists(os.path.join(dest, "aaa"))
