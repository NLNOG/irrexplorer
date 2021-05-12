# This is a temporary workaround till Poetry supports scripts, see
# https://github.com/sdispater/poetry/issues/241.
import asyncio
from subprocess import check_call

import uvicorn


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


def frontend_build() -> None:
    check_call(["yarn", "--cwd", "frontend/", "build"])


def frontend_install() -> None:
    check_call(["yarn", "--cwd", "frontend/"])


def import_data() -> None:
    from irrexplorer.commands import import_data as import_data_command
    asyncio.run(import_data_command.main())


def run_http() -> None:
    from irrexplorer.settings import HTTP_PORT, HTTP_WORKERS
    uvicorn.run('irrexplorer.app:app', port=HTTP_PORT, workers=HTTP_WORKERS)
