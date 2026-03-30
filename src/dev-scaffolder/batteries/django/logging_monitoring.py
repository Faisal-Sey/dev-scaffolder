import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_LOGGING_SETTINGS
from typings.base import ExecutorResponseStatus


class LoggingMonitoringBattery(BaseBattery):
    """
    Battery that configures Django's built-in logging.

    No packages are installed. Appends a LOGGING dict to settings.py that:
      - Formats log lines as: LEVEL TIMESTAMP MODULE MESSAGE
      - Writes logs to both console (stderr) and django.log in the project root
      - Root logger at WARNING; django logger at INFO
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'a') as f:
                f.write(DJANGO_LOGGING_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")
