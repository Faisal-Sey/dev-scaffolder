import os
import re
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import (
    DJANGO_POSTGRESQL_DATABASES,
    DJANGO_POSTGRESQL_ENV_EXAMPLE,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class PostgreSQLBattery(BaseBattery):
    """
    Battery that installs and configures PostgreSQL support for Django.

    Installs psycopg2-binary and python-dotenv, replaces the default SQLite
    DATABASES config with a PostgreSQL config driven by environment variables,
    and generates a .env.example file at the project root.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['psycopg2-binary', 'python-dotenv']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f"[bold red]Failed to install {package}[/bold red]")
                return ExecutorResponseStatus(success=False)
            self.console.print(f"[bold green]{package} installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            if 'import os' not in content:
                content = 'import os\n' + content
            content = re.sub(
                r"DATABASES\s*=\s*\{.*?\}[\s\n]*\}",
                DJANGO_POSTGRESQL_DATABASES,
                content,
                flags=re.DOTALL,
            )
            with open(settings_path, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

        with open(os.path.join(project_path, '.env.example'), 'w') as f:
            f.write(DJANGO_POSTGRESQL_ENV_EXAMPLE)
