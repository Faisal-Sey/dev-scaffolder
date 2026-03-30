import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_UNITTEST_TEST_EXAMPLE
from typings.base import ExecutorResponseStatus


class UnitTestBattery(BaseBattery):
    """
    Battery that scaffolds a Django unittest test structure.

    No packages are installed (unittest ships with Python and Django).
    Creates:
      tests/__init__.py
      tests/test_example.py  — sample Django TestCase
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        tests_dir = os.path.join(project_path, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        open(os.path.join(tests_dir, '__init__.py'), 'w').close()
        with open(os.path.join(tests_dir, 'test_example.py'), 'w') as f:
            f.write(DJANGO_UNITTEST_TEST_EXAMPLE)
        self.console.print("[bold green]unittest test structure written[/bold green]")
