# `stow-dploy` | Changelog

- **Update Poetry and VSCode Settings**: Update Poetry lockfile, add Poetry setup to GitHub actions, and update VSCode settings to use `ruff` and `pytest`.
- **Add Setup Scripts and Configurations**: Add `setup.cmd` for Windows setup and `launch.json` for Python in VSCode.
- **Improve Testing**: Fix tests, add `pytest-xdist` for faster parallelized testing, and skip remaining two tests that fail.
- **Enhance Code Quality**: Perform minor code cleanup, fix pylint warnings, migrate from `black` to `ruff`, and reformat Python files with `ruff`.
- **Refactor Codebase**: Use `makedirs` instead of `mkdir`, switch to `pathlib.Path.walk`, remove `pyfilesystem2` (`fs`) dependency entirely, and remove unused `conftest`.
- **Implement Type Safety**: Add type hints for stow functions, add type safety, add type hints to requirements, and perform type cleanup.
- **Update Project Configuration**: Move `pylint` config settings into `pyproject.toml`, update lock file and force a newer version of `Poetry`, and update formatting of pyproject.toml.
- **Remove Redundant Services and Files**: Remove AppVeyor and Travis as we only use GitHub action and remove unused `invoke.yml`.
- **Fix Issues**: Fix `create_tree` function, unix build, and ignore remaining `pylint` warnings.
- **Add New Features and Libraries**: Add Python packaging workflow, add `lexicon` library, install `pyenv` on Windows in `setup.cmd`, and add `tox` test pass.
