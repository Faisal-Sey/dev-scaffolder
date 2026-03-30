import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_GITLAB_CI
from typings.base import ExecutorResponseStatus


class GitLabCIBattery(BaseBattery):
    """
    Battery that adds a GitLab CI pipeline to the project.

    No packages are installed. Creates:
      .gitlab-ci.yml  — runs `python manage.py test` on main and merge requests.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, '.gitlab-ci.yml'), 'w') as f:
            f.write(DJANGO_GITLAB_CI)
        self.console.print("[bold green]GitLab CI pipeline written[/bold green]")
