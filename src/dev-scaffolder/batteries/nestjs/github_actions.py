import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import NESTJS_GITHUB_ACTIONS_WORKFLOW
from typings.base import ExecutorResponseStatus


class NestJSGitHubActionsBattery(BaseBattery):
    """
    Battery that adds a GitHub Actions CI workflow to a NestJS project.

    Creates .github/workflows/ci.yml that installs dependencies and runs
    the Jest test suite on every push and pull request to main.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        workflows_dir = os.path.join(project_path, '.github', 'workflows')
        os.makedirs(workflows_dir, exist_ok=True)
        with open(os.path.join(workflows_dir, 'ci.yml'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_GITHUB_ACTIONS_WORKFLOW)