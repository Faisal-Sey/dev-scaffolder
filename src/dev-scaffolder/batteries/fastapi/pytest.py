import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.fastapi.base import (
    FASTAPI_PYTEST_CONFTEST_PY,
    FASTAPI_PYTEST_TEST_MAIN_PY,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class FastAPIPytestBattery(BaseBattery):
    """
    Battery that adds pytest with async HTTP client support to a FastAPI project.

    Installs pytest, httpx, anyio[trio], pytest-anyio.
    Creates conftest.py with an AsyncClient fixture and tests/test_main.py.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['pytest', 'httpx', 'anyio[trio]', 'pytest-anyio']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f'[bold red]Failed to install {package}[/bold red]')
                return ExecutorResponseStatus(success=False)
            self.console.print(f'[bold green]{package} installed successfully[/bold green]')
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, 'conftest.py'), 'w') as f:
            f.write(FASTAPI_PYTEST_CONFTEST_PY)

        tests_dir = os.path.join(project_path, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        open(os.path.join(tests_dir, '__init__.py'), 'w').close()
        with open(os.path.join(tests_dir, 'test_main.py'), 'w') as f:
            f.write(FASTAPI_PYTEST_TEST_MAIN_PY)
