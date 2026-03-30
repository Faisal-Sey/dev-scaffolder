import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_BITBUCKET_PIPELINES
from typings.base import ExecutorResponseStatus


class BitbucketPipelinesBattery(BaseBattery):
    """
    Battery that adds a Bitbucket Pipelines configuration to the project.

    No packages are installed. Creates:
      bitbucket-pipelines.yml  — runs `python manage.py test` on all branches
                                 and specifically on main.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, 'bitbucket-pipelines.yml'), 'w') as f:
            f.write(DJANGO_BITBUCKET_PIPELINES)
        self.console.print("[bold green]Bitbucket Pipelines configuration written[/bold green]")
