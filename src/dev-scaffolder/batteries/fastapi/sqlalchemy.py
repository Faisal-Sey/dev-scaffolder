import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.fastapi.base import (
    FASTAPI_SQLALCHEMY_DATABASE_PY,
    FASTAPI_SQLALCHEMY_IMPORTS,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class FastAPISQLAlchemyBattery(BaseBattery):
    """
    Battery that adds async SQLAlchemy to a FastAPI project.

    Installs sqlalchemy[asyncio], aiosqlite, asyncpg, alembic.
    Creates app/database.py with engine, session factory, Base, and get_db dependency.
    Inserts the get_db import marker into main.py.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['sqlalchemy[asyncio]', 'aiosqlite', 'asyncpg', 'alembic']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f'[bold red]Failed to install {package}[/bold red]')
                return ExecutorResponseStatus(success=False)
            self.console.print(f'[bold green]{package} installed successfully[/bold green]')
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_dir = os.path.join(project_path, 'app')

        with open(os.path.join(app_dir, 'database.py'), 'w') as f:
            f.write(FASTAPI_SQLALCHEMY_DATABASE_PY)

        main_py = os.path.join(app_dir, 'main.py')
        try:
            with open(main_py, 'r') as f:
                content = f.read()
            content = content.replace(
                '# [BATTERY:IMPORTS]',
                f'{FASTAPI_SQLALCHEMY_IMPORTS}# [BATTERY:IMPORTS]',
            )
            with open(main_py, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {main_py}[/bold red]')
