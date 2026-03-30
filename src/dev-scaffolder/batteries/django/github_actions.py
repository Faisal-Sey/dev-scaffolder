import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_GITHUB_ACTIONS_WORKFLOW
from typings.base import ExecutorResponseStatus


class GitHubActionsBattery(BaseBattery):
    """
    Battery that adds a GitHub Actions CI workflow to the project.

    No packages are installed. Creates:
      .github/workflows/django.yml  — checks out code, installs requirements,
                                      and runs `python manage.py test` on push/PR
                                      to main.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        workflows_dir = os.path.join(project_path, '.github', 'workflows')
        os.makedirs(workflows_dir, exist_ok=True)
        with open(os.path.join(workflows_dir, 'django.yml'), 'w') as f:
            f.write(DJANGO_GITHUB_ACTIONS_WORKFLOW)
        self.console.print("[bold green]GitHub Actions workflow written[/bold green]")
