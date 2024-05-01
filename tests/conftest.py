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
def dest(tmp_path: Path) -> Generator[str, None, None]:
    """
    a destination directory to stow into or unstow from
    """
    name = str(tmp_path.joinpath("dest"))
    utils.create_directory(name)
    yield name
    utils.restore_tree_permissions(tmp_path)


@pytest.fixture()
def file_a(tmp_path: Path) -> str:
    """
    creates a file
    """
    return utils.create_file(tmp_path.joinpath("file_a"))


@pytest.fixture()
def file_b(tmp_path: Path) -> str:
    """
    creates a file
    """
    return utils.create_file(tmp_path.joinpath("file_b"))


@pytest.fixture()
def file_dploystowignore(tmp_path: Path) -> str:
    """
    creates an empty ignore file file
    """
    return utils.create_file(tmp_path.joinpath(".dploystowignore"))
