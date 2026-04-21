import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus

FASTAPI_CIRCLECI_CONFIG = """\
version: 2.1

orbs:
  python: circleci/python@2

jobs:
  test:
    executor: python/default
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
      - run:
          name: Run tests
          command: pytest

workflows:
  test:
    jobs:
      - test
"""


class FastAPICircleCIBattery(BaseBattery):
    """
    Battery that adds a CircleCI pipeline config to a FastAPI project.

    Creates .circleci/config.yml that installs pip packages and runs pytest
    using the circleci/python@2 orb.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        circleci_dir = os.path.join(project_path, '.circleci')
        os.makedirs(circleci_dir, exist_ok=True)
        with open(os.path.join(circleci_dir, 'config.yml'), 'w', encoding='utf-8') as f:
            f.write(FASTAPI_CIRCLECI_CONFIG)