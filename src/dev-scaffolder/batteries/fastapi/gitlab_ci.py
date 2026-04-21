import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus

FASTAPI_GITLAB_CI = """\
image: python:3.12-slim

stages:
  - test

test:
  stage: test
  cache:
    paths:
      - .pip-cache/
  variables:
    PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"
  before_script:
    - pip install -r requirements.txt
  script:
    - pytest
  only:
    - main
    - merge_requests
"""


class FastAPIGitLabCIBattery(BaseBattery):
    """
    Battery that adds a GitLab CI pipeline to a FastAPI project.

    Creates .gitlab-ci.yml that installs pip dependencies and runs pytest
    on main and merge requests.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, '.gitlab-ci.yml'), 'w', encoding='utf-8') as f:
            f.write(FASTAPI_GITLAB_CI)