import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_CORS_SETTINGS
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class CorsHeadersBattery(BaseBattery):
    """
    Battery that installs and configures django-cors-headers.

    Adds 'corsheaders' to INSTALLED_APPS before any custom app,
    inserts CorsMiddleware before CommonMiddleware, and appends
    CORS settings to settings.py.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'django-cors-headers']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install django-cors-headers[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]django-cors-headers installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            if app_name:
                content = self._insert_app_before(content, 'corsheaders', app_name)
            else:
                content = self._insert_app_re(content, 'corsheaders')
            content = self._insert_before_common_middleware(
                content, 'corsheaders.middleware.CorsMiddleware'
            )
            with open(settings_path, 'w') as f:
                f.write(content)
            with open(settings_path, 'a') as f:
                f.write(DJANGO_CORS_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")
