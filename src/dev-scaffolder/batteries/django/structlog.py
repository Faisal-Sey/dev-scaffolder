import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_STRUCTLOG_SETTINGS
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class StructlogBattery(BaseBattery):
    """
    Battery that installs and configures structlog for structured logging.

    Installs structlog, then appends structlog.configure() to settings.py
    with console rendering and ISO timestamp formatting.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'structlog']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install structlog[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]structlog installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'a') as f:
                f.write(DJANGO_STRUCTLOG_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")
