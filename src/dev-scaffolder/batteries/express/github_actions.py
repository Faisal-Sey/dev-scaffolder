import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.express.base import EXPRESS_GITHUB_ACTIONS_WORKFLOW
from typings.base import ExecutorResponseStatus


class ExpressGitHubActionsBattery(BaseBattery):
    """
    Battery that adds a GitHub Actions CI workflow to an Express project.

    No packages are installed. Creates:
      .github/workflows/ci.yml  -- installs deps with npm ci and runs npm test
                                   on push/PR to main.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        workflows_dir = os.path.join(project_path, '.github', 'workflows')
        os.makedirs(workflows_dir, exist_ok=True)
        with open(os.path.join(workflows_dir, 'ci.yml'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_GITHUB_ACTIONS_WORKFLOW)
        self.console.print('[bold green]GitHub Actions workflow written[/bold green]')
