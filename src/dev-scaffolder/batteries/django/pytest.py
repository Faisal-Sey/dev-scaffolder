import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_PYTEST_CONFTEST, DJANGO_PYTEST_TEST_EXAMPLE
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class PytestBattery(BaseBattery):
    """
    Battery that installs and configures pytest for a Django project.

    - Installs pytest and pytest-django
    - Writes pytest.ini with DJANGO_SETTINGS_MODULE
    - Writes conftest.py at the project root
    - Creates tests/ with an example test file
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['pytest', 'pytest-django']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f"[bold red]Failed to install {package}[/bold red]")
                return ExecutorResponseStatus(success=False)
            self.console.print(f"[bold green]{package} installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        pytest_ini = (
            "[pytest]\n"
            f"DJANGO_SETTINGS_MODULE = {project_name}.settings\n"
            "python_files = tests.py test_*.py *_tests.py\n"
            "python_classes = Test*\n"
            "python_functions = test_*\n"
        )
        with open(os.path.join(project_path, 'pytest.ini'), 'w') as f:
            f.write(pytest_ini)

        with open(os.path.join(project_path, 'conftest.py'), 'w') as f:
            f.write(DJANGO_PYTEST_CONFTEST)

        tests_dir = os.path.join(project_path, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        open(os.path.join(tests_dir, '__init__.py'), 'w').close()
        with open(os.path.join(tests_dir, 'test_example.py'), 'w') as f:
            f.write(DJANGO_PYTEST_TEST_EXAMPLE)
