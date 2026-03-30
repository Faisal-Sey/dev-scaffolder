import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_CIRCLECI_CONFIG
from typings.base import ExecutorResponseStatus


class CircleCIBattery(BaseBattery):
    """
    Battery that adds a CircleCI pipeline configuration to the project.

    No packages are installed. Creates:
      .circleci/config.yml  — runs `python manage.py test` using cimg/python:3.12.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        circleci_dir = os.path.join(project_path, '.circleci')
        os.makedirs(circleci_dir, exist_ok=True)
        with open(os.path.join(circleci_dir, 'config.yml'), 'w') as f:
            f.write(DJANGO_CIRCLECI_CONFIG)
        self.console.print("[bold green]CircleCI configuration written[/bold green]")
