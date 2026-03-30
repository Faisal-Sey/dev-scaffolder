import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.fastapi.base import (
    FASTAPI_SENTRY_IMPORT,
    FASTAPI_SENTRY_SETUP,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class FastAPISentryBattery(BaseBattery):
    """
    Battery that adds Sentry error monitoring to a FastAPI project.

    Installs sentry-sdk[fastapi].
    Inserts sentry_sdk.init() into main.py via the [BATTERY:IMPORTS] marker.
    Set SENTRY_DSN in your environment to activate.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'sentry-sdk[fastapi]']
        if not run_subprocess_command(command):
            self.console.print('[bold red]Failed to install sentry-sdk[/bold red]')
            return ExecutorResponseStatus(success=False)
        self.console.print('[bold green]sentry-sdk installed successfully[/bold green]')
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        main_py = os.path.join(project_path, 'app', 'main.py')
        try:
            with open(main_py, 'r') as f:
                content = f.read()
            content = content.replace(
                '# [BATTERY:IMPORTS]',
                f'{FASTAPI_SENTRY_IMPORT}# [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '# [BATTERY:MIDDLEWARE]',
                f'{FASTAPI_SENTRY_SETUP}# [BATTERY:MIDDLEWARE]',
            )
            with open(main_py, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {main_py}[/bold red]')
