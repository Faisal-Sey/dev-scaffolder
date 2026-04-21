import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus

FASTAPI_BITBUCKET_PIPELINES = """\
image: python:3.12-slim

pipelines:
  default:
    - step:
        name: Test
        caches:
          - pip
        script:
          - pip install -r requirements.txt
          - pytest
  branches:
    main:
      - step:
          name: Test
          caches:
            - pip
          script:
            - pip install -r requirements.txt
            - pytest
"""


class FastAPIBitbucketPipelinesBattery(BaseBattery):
    """
    Battery that adds a Bitbucket Pipelines config to a FastAPI project.

    Creates bitbucket-pipelines.yml that installs pip dependencies and runs
    pytest on every push, with pip cache.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(
            os.path.join(project_path, 'bitbucket-pipelines.yml'), 'w', encoding='utf-8'
        ) as f:
            f.write(FASTAPI_BITBUCKET_PIPELINES)