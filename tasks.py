"""
Project Tasks that can be invoked using using the program "invoke" or "inv"
"""

import os

from invoke import Context, task  # type: ignore

IS_WINDOWS = os.name == "nt"
if IS_WINDOWS:
    # setting 'shell' is a work around for issue #345 of invoke
    RUN_ARGS = {"pty": False, "shell": "C:\\Windows\\System32\\cmd.exe"}
else:
    RUN_ARGS = {"pty": True}


def get_files():
    """Get the files to run analysis on"""
    files = [
        "dploy",
        "tests",
        "tasks.py",
    ]
    files_string = " ".join(files)
    return files_string


@task
def setup(ctx: Context):
    """Install python requirements"""
    ctx.run("python -m pip install -r requirements.txt", **RUN_ARGS)


@task
def clean(ctx: Context):
    """Clean repository using git"""
    ctx.run("git clean --interactive", **RUN_ARGS)


@task
def lint(ctx: Context):
    """Run pylint on this module"""
    cmds = ["pylint --output-format=parseable", "ruff"]
    base_cmd = "python -m {cmd} {files}"

    for cmd in cmds:
        ctx.run(base_cmd.format(cmd=cmd, files=get_files()), **RUN_ARGS)


@task
def reformat_check(ctx: Context):
    """Run formatting check"""
    cmd = "ruff format --check"
    base_cmd = "python -m {cmd} {files}"
    ctx.run(base_cmd.format(cmd=cmd, files=get_files()), **RUN_ARGS)


@task
def reformat(ctx: Context):
    """Run formatting"""
    cmd = "ruff format"
    base_cmd = "python -m {cmd} {files}"
    ctx.run(base_cmd.format(cmd=cmd, files=get_files()), **RUN_ARGS)


@task
def metrics(ctx: Context):
    """Run radon code metrics on this module"""
    cmd = "radon {metric} --min B {files}"
    metrics_to_run = ["cc", "mi"]
    for metric in metrics_to_run:
        ctx.run(cmd.format(metric=metric, files=get_files()), **RUN_ARGS)


@task()
def test(ctx: Context):
    """Run 'pytest' on package.

    We use 'py.test' instead of the recommended pytest so it works on Python v3.3 release."""
    cmd = "py.test --cov-report term-missing --cov=dploy --color=no"
    ctx.run(cmd, **RUN_ARGS)


@task(clean)
def build(ctx: Context):
    """Task to build an executable using pyinstaller"""
    cmd = "pyinstaller --clean --noconfirm --name dploy --onefile " + os.path.join("dploy", "__main__.py")
    ctx.run(cmd, **RUN_ARGS)


@task(test, lint, reformat_check)
def all(default=True):  # pylint: disable=redefined-builtin,unused-argument
    """Run all critical tasks."""
