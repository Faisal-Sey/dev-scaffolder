import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import NESTJS_CIRCLECI_CONFIG
from typings.base import ExecutorResponseStatus


class NestJSCircleCIBattery(BaseBattery):
    """
    Battery that adds a CircleCI pipeline config to a NestJS project.

    Creates .circleci/config.yml that installs npm packages and runs
    the Jest test suite using the circleci/node@5 orb.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        circleci_dir = os.path.join(project_path, '.circleci')
        os.makedirs(circleci_dir, exist_ok=True)
        with open(os.path.join(circleci_dir, 'config.yml'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_CIRCLECI_CONFIG)