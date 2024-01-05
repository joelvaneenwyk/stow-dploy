"""
Contains the fixtures used by the dploy tests
"""

from pathlib import Path
from typing import Generator

import pytest

from tests import utils


@pytest.fixture()
def source_a(tmp_path: Path) -> Generator[str, None, None]:
    """
    a source directory to stow and unstow
    """
    name = str(tmp_path / "source_a")
    tree: utils.StowTree = [
        {
            name: [
                {
                    "aaa": [
                        "aaa",
                        "bbb",
                        {
                            "ccc": [
                                "aaa",
                                "bbb",
                            ],
                        },
                    ],
                },
            ],
        }
    ]
    utils.create_tree(tree)
    yield name
    utils.restore_tree_permissions(tmp_path)


@pytest.fixture()
def source_b(tmp_path: Path) -> Generator[str, None, None]:
    """
    a source directory to stow and unstow
    """
    name = str(tmp_path / "source_b")
    tree: utils.StowTree = [
        {
            name: [
                {
                    "aaa": [
                        "ddd",
                        "eee",
                        {
                            "fff": [
                                "aaa",
                                "bbb",
                            ],
                        },
                    ],
                },
            ],
        },
    ]
    utils.create_tree(tree)
    yield name
    utils.restore_tree_permissions(tmp_path)


@pytest.fixture()
def source_d(tmp_path: Path) -> Generator[str, None, None]:
    """
    a source directory to stow and unstow
    """
    name = str(tmp_path / "source_d")
    tree: utils.StowTree = [
        {
            name: [
                {
                    "aaa": [
                        "ggg",
                        "hhh",
                        {
                            "iii": [
                                "aaa",
                                "bbb",
                            ],
                        },
                    ],
                },
            ],
        },
    ]
    utils.create_tree(tree)
    yield name
    utils.restore_tree_permissions(tmp_path)


@pytest.fixture()
def source_c(tmp_path: Path) -> Generator[str, None, None]:
    """
    a source directory to stow and unstow identical to source_a
    """
    name = str(tmp_path / "source_c")
    tree: utils.StowTree = [
        {
            name: [
                {
                    "aaa": [
                        "aaa",
                        "bbb",
                        {
                            "ccc": [
                                "aaa",
                                "bbb",
                            ],
                        },
                    ],
                },
            ],
        },
    ]
    utils.create_tree(tree)
    yield name
    utils.restore_tree_permissions(tmp_path)


@pytest.fixture()
def source_only_files(tmp_path: Path) -> Generator[str, None, None]:
    """
    a source directory to stow and unstow that only contains files
    """
    name = str(tmp_path / "source_only_files")
    tree: utils.StowTree = [
        {
            name: [
                "aaa",
            ]
        }
    ]
    utils.create_tree(tree)
    yield name
    utils.restore_tree_permissions(tmp_path)


@pytest.fixture()
def dest(tmpdir) -> Generator[str, None, None]:
    """
    a destination directory to stow into or unstow from
    """
    name = str(tmpdir.join("dest"))
    utils.create_directory(name)
    yield name
    utils.restore_tree_permissions(tmpdir)


@pytest.fixture()
def file_a(tmpdir):
    """
    creates a file
    """
    name = str(tmpdir.join("file_a"))
    utils.create_file(name)
    return name


@pytest.fixture()
def file_b(tmpdir):
    """
    creates a file
    """
    name = str(tmpdir.join("file_b"))
    utils.create_file(name)
    return name


@pytest.fixture()
def file_dploystowignore(tmpdir):
    """
    creates an empty ignore file file
    """
    name = str(tmpdir.join(".dploystowignore"))
    utils.create_file(name)
    return name
