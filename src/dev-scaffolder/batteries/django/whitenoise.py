import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_WHITENOISE_SETTINGS
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class WhitenoiseBattery(BaseBattery):
    """
    Battery that installs and configures whitenoise for static file serving.

    - Installs whitenoise
    - Adds 'whitenoise.runserver_nostatic' to INSTALLED_APPS before
      'django.contrib.staticfiles' so development serving is handled correctly
    - Inserts WhiteNoiseMiddleware right after SecurityMiddleware
    - Appends STATIC_ROOT, STATICFILES_DIRS, and STATICFILES_STORAGE to settings.py
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'whitenoise']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install whitenoise[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]whitenoise installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'r') as f:
                content = f.read()

            content = self._insert_app_before(
                content,
                'whitenoise.runserver_nostatic',
                'django.contrib.staticfiles',
            )
            content = self._insert_after_security_middleware(
                content,
                'whitenoise.middleware.WhiteNoiseMiddleware',
            )

            with open(settings_path, 'w') as f:
                f.write(content)
            with open(settings_path, 'a') as f:
                f.write(DJANGO_WHITENOISE_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")
