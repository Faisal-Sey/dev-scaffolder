import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.express.base import EXPRESS_BITBUCKET_PIPELINES
from typings.base import ExecutorResponseStatus


class ExpressBitbucketPipelinesBattery(BaseBattery):
    """
    Battery that adds a Bitbucket Pipelines configuration to an Express project.

    No packages are installed. Creates:
      bitbucket-pipelines.yml  -- runs npm ci and npm test on all branches
                                  and specifically on main.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, 'bitbucket-pipelines.yml'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_BITBUCKET_PIPELINES)
        self.console.print('[bold green]Bitbucket Pipelines configuration written[/bold green]')
