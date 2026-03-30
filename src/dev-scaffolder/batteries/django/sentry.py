import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_SENTRY_SETTINGS
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class SentryBattery(BaseBattery):
    """
    Battery that installs and configures the Sentry SDK for Django.

    Installs sentry-sdk[django], then appends sentry_sdk.init() to settings.py.
    Set the SENTRY_DSN environment variable to activate error reporting.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'sentry-sdk[django]']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install sentry-sdk[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]sentry-sdk installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'a') as f:
                f.write(DJANGO_SENTRY_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")
