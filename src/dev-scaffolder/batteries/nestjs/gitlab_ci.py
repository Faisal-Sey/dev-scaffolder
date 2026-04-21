import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import NESTJS_GITLAB_CI
from typings.base import ExecutorResponseStatus


class NestJSGitLabCIBattery(BaseBattery):
    """
    Battery that adds a GitLab CI pipeline to a NestJS project.

    Creates .gitlab-ci.yml that installs dependencies and runs the Jest
    test suite on main and merge requests.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, '.gitlab-ci.yml'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_GITLAB_CI)