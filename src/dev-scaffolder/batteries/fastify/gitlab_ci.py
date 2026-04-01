import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.fastify.base import FASTIFY_GITLAB_CI
from typings.base import ExecutorResponseStatus


class FastifyGitLabCIBattery(BaseBattery):
    """
    Battery that adds a GitLab CI pipeline to a Fastify project.

    No packages are installed. Creates:
      .gitlab-ci.yml  -- installs deps and runs npm test on main and MRs.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, '.gitlab-ci.yml'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_GITLAB_CI)
        self.console.print('[bold green]GitLab CI config written[/bold green]')
