import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

from executors.backend.python.django.batteries.base import BaseBattery
from constants.backend.python.base import (
    DJANGO_DRF_SETTINGS,
    DJANGO_DRF_SERIALIZER,
    DJANGO_DRF_VIEW,
    DJANGO_DRF_URL_CONFIG,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class RestFrameworkBattery(BaseBattery):
    """
    Battery that installs and configures Django REST Framework.

    Adds 'rest_framework' to INSTALLED_APPS, appends DRF pagination settings,
    and (when an app name is provided) creates a starter serializer, APIView,
    and URL configuration inside the app directory.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'djangorestframework']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install djangorestframework[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]djangorestframework installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            content = self._insert_app_re(content, 'rest_framework')
            with open(settings_path, 'w') as f:
                f.write(content)
            with open(settings_path, 'a') as f:
                f.write(DJANGO_DRF_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")
            return

        if not app_name:
            return

        app_path = os.path.join(project_path, app_name)
        with open(os.path.join(app_path, 'serializers.py'), 'w') as f:
            f.write(DJANGO_DRF_SERIALIZER)
        with open(os.path.join(app_path, 'views.py'), 'w') as f:
            f.write(DJANGO_DRF_VIEW)
        with open(os.path.join(app_path, 'urls.py'), 'w') as f:
            f.write(DJANGO_DRF_URL_CONFIG)
