# `stow-dploy` | Changelog

- **Update Poetry and VSCode Settings**: Update Poetry lock, setup Poetry in GitHub action workflow, and update VSCode settings to use `ruff` and enable `pytest` in the editor.
- **Add Setup Scripts and Configurations**: Add `setup.cmd` for Windows setup, `launch.json` for Python, and update setup script to only call sudo when needed.
- **Improve Testing**: Fix tests, add `pytest-xdist` for faster parallelized testing, and skip remaining two tests that fail.
- **Enhance Code Quality**: Perform minor code cleanup, fix pylint warnings, migrate from `black` to `ruff`, and reformat Python files with `ruff`.
- **Refactor Codebase**: Use `makedirs` instead of `mkdir`, switch to `pathlib.Path.walk`, remove pyfilesystem2 (`fs`) dependency entirely, and remove useless conftest.
- **Implement Type Safety**: Add type hints for stow functions, add type safety, add type hints to requirements, and perform type cleanup.
- **Update Project Configuration**: Move `pylint` config settings into `pyproject.toml`, update lock file and force a newer version of Poetry, and update formatting of pyproject.toml.
- **Remove Redundant Services and Files**: Remove AppVeyor and Travis as we only use GitHub actions, remove build from invoke all, remove extra test files, and remove `invoke.yml`.
- **Fix Issues**: Fix create_tree function, fix remaining issues, fix unix build, and ignore remaining pylint warnings.
- **Add New Features and Libraries**: Add Python packaging workflow, add lexicon library to requirements, install pyenv on Windows, and add tox test.
