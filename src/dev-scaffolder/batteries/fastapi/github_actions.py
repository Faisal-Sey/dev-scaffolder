import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus

FASTAPI_GITHUB_ACTIONS_WORKFLOW = """\
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest
"""


class FastAPIGitHubActionsBattery(BaseBattery):
    """
    Battery that adds a GitHub Actions CI workflow to a FastAPI project.

    Creates .github/workflows/ci.yml that installs pip dependencies and
    runs the pytest test suite on every push and pull request to main.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        workflows_dir = os.path.join(project_path, '.github', 'workflows')
        os.makedirs(workflows_dir, exist_ok=True)
        with open(os.path.join(workflows_dir, 'ci.yml'), 'w', encoding='utf-8') as f:
            f.write(FASTAPI_GITHUB_ACTIONS_WORKFLOW)