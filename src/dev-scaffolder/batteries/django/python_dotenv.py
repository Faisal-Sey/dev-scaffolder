import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import (
    DJANGO_DOTENV_IMPORT,
    DJANGO_DOTENV_ENV_EXAMPLE,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class PythonDotenvBattery(BaseBattery):
    """
    Battery that installs python-dotenv and wires it into Django settings.

    Inserts a load_dotenv() call immediately after the pathlib import so that
    all os.environ.get() calls in settings.py resolve from the .env file.
    Appends a starter .env.example with SECRET_KEY, DEBUG, and ALLOWED_HOSTS.

    Works well alongside PostgreSQLBattery — load_dotenv() makes DB_* vars
    available before the DATABASES config reads them.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'python-dotenv']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install python-dotenv[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]python-dotenv installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            # Insert load_dotenv() right after the pathlib import
            content = content.replace(
                'from pathlib import Path',
                'from pathlib import Path' + DJANGO_DOTENV_IMPORT,
                1,
            )
            with open(settings_path, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

        # Append to .env.example — creates it if it doesn't exist yet
        with open(os.path.join(project_path, '.env.example'), 'a') as f:
            f.write(DJANGO_DOTENV_ENV_EXAMPLE)
