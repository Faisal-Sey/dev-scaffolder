import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_CELERY_SETTINGS, DJANGO_CELERY_TASK_EXAMPLE
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class CeleryBattery(BaseBattery):
    """
    Battery that installs and configures Celery with a Redis broker.

    - Installs celery[redis]
    - Writes {project_name}/celery.py (Celery app bootstrap)
    - Patches {project_name}/__init__.py to expose celery_app at package level
    - Appends CELERY_* settings to settings.py
    - Writes {app_name}/tasks.py with sample tasks (if app_name is provided)
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'celery[redis]']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install celery[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]celery[redis] installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def _write_celery_app(self, project_path: str, project_name: str) -> None:
        celery_py = (
            "import os\n"
            "from celery import Celery\n\n"
            f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')\n\n"
            f"app = Celery('{project_name}')\n"
            "app.config_from_object('django.conf:settings', namespace='CELERY')\n"
            "app.autodiscover_tasks()\n"
        )
        with open(os.path.join(project_path, project_name, 'celery.py'), 'w') as f:
            f.write(celery_py)

    def _patch_init_py(self, project_path: str, project_name: str) -> None:
        init_path = os.path.join(project_path, project_name, '__init__.py')
        celery_import = (
            "from .celery import app as celery_app\n\n"
            "__all__ = ('celery_app',)\n"
        )
        try:
            with open(init_path, 'r') as f:
                existing = f.read()
            if 'celery_app' not in existing:
                with open(init_path, 'w') as f:
                    f.write(celery_import + existing)
        except FileNotFoundError:
            with open(init_path, 'w') as f:
                f.write(celery_import)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        settings_path = os.path.join(project_path, project_name, 'settings.py')

        self._write_celery_app(project_path, project_name)
        self._patch_init_py(project_path, project_name)

        try:
            with open(settings_path, 'a') as f:
                f.write(DJANGO_CELERY_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")
            return

        if app_name:
            tasks_path = os.path.join(project_path, app_name, 'tasks.py')
            with open(tasks_path, 'w') as f:
                f.write(DJANGO_CELERY_TASK_EXAMPLE)
