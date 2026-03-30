import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.express.base import EXPRESS_CIRCLECI_CONFIG
from typings.base import ExecutorResponseStatus


class ExpressCircleCIBattery(BaseBattery):
    """
    Battery that adds a CircleCI pipeline configuration to an Express project.

    No packages are installed. Creates:
      .circleci/config.yml  -- installs deps via the node orb and runs npm test.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        circleci_dir = os.path.join(project_path, '.circleci')
        os.makedirs(circleci_dir, exist_ok=True)
        with open(os.path.join(circleci_dir, 'config.yml'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_CIRCLECI_CONFIG)
        self.console.print('[bold green]CircleCI configuration written[/bold green]')
