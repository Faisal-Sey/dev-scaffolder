import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.fastapi.base import (
    FASTAPI_TORTOISE_CONFIG_PY,
    FASTAPI_TORTOISE_MODELS_PY,
    FASTAPI_TORTOISE_REGISTER_CODE,
    FASTAPI_TORTOISE_LIFESPAN,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class FastAPITortoiseORMBattery(BaseBattery):
    """
    Battery that adds Tortoise ORM (async) to a FastAPI project.

    Installs tortoise-orm and aerich.
    Creates app/tortoise_config.py and app/models.py.
    Patches main.py with RegisterTortoise lifespan and import markers.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['tortoise-orm[asyncpg]', 'aerich']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f'[bold red]Failed to install {package}[/bold red]')
                return ExecutorResponseStatus(success=False)
            self.console.print(f'[bold green]{package} installed successfully[/bold green]')
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_dir = os.path.join(project_path, 'app')

        with open(os.path.join(app_dir, 'tortoise_config.py'), 'w') as f:
            f.write(FASTAPI_TORTOISE_CONFIG_PY)

        with open(os.path.join(app_dir, 'models.py'), 'w') as f:
            f.write(FASTAPI_TORTOISE_MODELS_PY)

        main_py = os.path.join(app_dir, 'main.py')
        try:
            with open(main_py, 'r') as f:
                content = f.read()
            content = content.replace(
                '# [BATTERY:IMPORTS]',
                f'{FASTAPI_TORTOISE_REGISTER_CODE}{FASTAPI_TORTOISE_LIFESPAN}# [BATTERY:IMPORTS]',
            )
            # Add lifespan= to FastAPI constructor
            content = content.replace(
                'app = FastAPI(',
                'app = FastAPI(\n    lifespan=lifespan,',
            )
            with open(main_py, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {main_py}[/bold red]')
