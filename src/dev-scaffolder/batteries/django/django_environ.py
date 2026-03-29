import os
import re
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import (
    DJANGO_ENVIRON_SETUP,
    DJANGO_ENVIRON_ENV_EXAMPLE,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class DjangoEnvironBattery(BaseBattery):
    """
    Battery that installs django-environ and wires it into Django settings.

    Inserts the environ.Env setup after BASE_DIR and replaces the hardcoded
    SECRET_KEY, DEBUG, and ALLOWED_HOSTS values with env() calls so they
    are driven entirely by a .env file. Appends a starter .env.example.

    Use this instead of PythonDotenvBattery when you want full django-environ
    integration rather than just load_dotenv().
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'django-environ']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install django-environ[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]django-environ installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'r') as f:
                content = f.read()

            # Insert environ setup immediately after the BASE_DIR definition
            content = content.replace(
                'BASE_DIR = Path(__file__).resolve().parent.parent',
                'BASE_DIR = Path(__file__).resolve().parent.parent' + DJANGO_ENVIRON_SETUP,
                1,
            )

            # Replace hardcoded SECRET_KEY with env() call
            content = re.sub(
                r"SECRET_KEY\s*=\s*['\"].*?['\"]",
                "SECRET_KEY = env('SECRET_KEY')",
                content,
            )

            # Replace hardcoded DEBUG with env.bool() call
            content = re.sub(
                r"DEBUG\s*=\s*(True|False)",
                "DEBUG = env.bool('DEBUG', default=False)",
                content,
            )

            # Replace hardcoded ALLOWED_HOSTS with env.list() call
            content = re.sub(
                r"ALLOWED_HOSTS\s*=\s*\[.*?\]",
                "ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])",
                content,
                flags=re.DOTALL,
            )

            with open(settings_path, 'w') as f:
                f.write(content)

        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

        # Append to .env.example — creates it if it doesn't exist yet
        with open(os.path.join(project_path, '.env.example'), 'a') as f:
            f.write(DJANGO_ENVIRON_ENV_EXAMPLE)
