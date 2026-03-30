import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_COVERAGE_RC
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class CoverageBattery(BaseBattery):
    """
    Battery that installs coverage and configures it for a Django project.

    Installs coverage and pytest-cov, then writes:
      .coveragerc  — omits migrations, venv, manage.py, and settings files
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['coverage', 'pytest-cov']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f"[bold red]Failed to install {package}[/bold red]")
                return ExecutorResponseStatus(success=False)
            self.console.print(f"[bold green]{package} installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, '.coveragerc'), 'w') as f:
            f.write(DJANGO_COVERAGE_RC)
        self.console.print("[bold green].coveragerc written[/bold green]")
