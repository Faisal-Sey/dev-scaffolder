import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.fastapi.base import (
    FASTAPI_CELERY_APP_PY,
    FASTAPI_CELERY_TASKS_PY,
)
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class FastAPICeleryBattery(BaseBattery):
    """
    Battery that adds Celery with a Redis broker to a FastAPI project.

    Installs celery[redis].
    Creates app/celery_app.py and app/tasks.py.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'celery[redis]']
        if not run_subprocess_command(command):
            self.console.print('[bold red]Failed to install celery[/bold red]')
            return ExecutorResponseStatus(success=False)
        self.console.print('[bold green]celery[redis] installed successfully[/bold green]')
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_dir = os.path.join(project_path, 'app')
        with open(os.path.join(app_dir, 'celery_app.py'), 'w') as f:
            f.write(FASTAPI_CELERY_APP_PY)
        with open(os.path.join(app_dir, 'tasks.py'), 'w') as f:
            f.write(FASTAPI_CELERY_TASKS_PY)
