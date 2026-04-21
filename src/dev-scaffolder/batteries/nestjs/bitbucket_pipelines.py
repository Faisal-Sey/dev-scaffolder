import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import NESTJS_BITBUCKET_PIPELINES
from typings.base import ExecutorResponseStatus


class NestJSBitbucketPipelinesBattery(BaseBattery):
    """
    Battery that adds a Bitbucket Pipelines config to a NestJS project.

    Creates bitbucket-pipelines.yml that installs dependencies and runs the
    Jest test suite on every push, with caching for node_modules.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(
            os.path.join(project_path, 'bitbucket-pipelines.yml'), 'w', encoding='utf-8'
        ) as f:
            f.write(NESTJS_BITBUCKET_PIPELINES)