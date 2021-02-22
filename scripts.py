# This is a temporary workaround till Poetry supports scripts, see
# https://github.com/sdispater/poetry/issues/241.
from subprocess import check_call


def reformat() -> None:
    check_call(
        ["black", "-l 100", "irrexplorer/"],
    )
    check_call(
        ["isort", "-l 100", "-m", "VERTICAL_HANGING_INDENT", "--tc", "irrexplorer/"],
    )


def lint() -> None:
    check_call(["flake8", "irrexplorer/"])
    check_call(["mypy", "irrexplorer/"])


def build() -> None:
    check_call(["yarn", "--cwd", "frontend/", "build"])


def frontend_install() -> None:
    check_call(["yarn", "--cwd", "frontend/"])
