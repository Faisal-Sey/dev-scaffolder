import os
import re
import sys
from abc import ABC, abstractmethod

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

from rich.console import Console
from typings.base import ExecutorResponseStatus


class BaseBattery(ABC):
    """
    Abstract base class for Django project batteries.

    A battery encapsulates an optional dependency (e.g. djangorestframework,
    django-cors-headers, psycopg2) that can be selectively applied to a
    scaffolded Django project. Each battery is responsible for installing
    its own packages and configuring the project's settings/files.
    """

    def __init__(self):
        self.console = Console()

    def _insert_app_re(self, content: str, new_app: str) -> str:
        """Insert a new app entry into the INSTALLED_APPS list using regex."""
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'

        def insert_app(match):
            prefix = match.group(1)
            apps_content = match.group(2)
            suffix = match.group(3)
            apps_content = apps_content.rstrip()
            if apps_content.strip():
                if not apps_content.strip().endswith(','):
                    apps_content += ','
                return f"{prefix}{apps_content}\n    '{new_app}',\n{suffix}"
            return f"{prefix}\n    '{new_app}',\n{suffix}"

        return re.sub(pattern, insert_app, content, flags=re.DOTALL)

    def _insert_before_common_middleware(self, content: str, middleware: str) -> str:
        """Insert a middleware entry immediately before CommonMiddleware."""
        return content.replace(
            "    'django.middleware.common.CommonMiddleware',",
            f"    '{middleware}',\n    'django.middleware.common.CommonMiddleware',"
        )

    @abstractmethod
    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        """
        Install the packages required by this battery.

        :param venv_python_executor: Path to the venv Python executable.
        :return: ExecutorResponseStatus indicating success or failure.
        """
        ...

    @abstractmethod
    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        """
        Apply configuration changes to the scaffolded Django project.

        :param project_path: Absolute path to the root of the Django project.
        :param project_name: Django project package name (used to locate settings.py).
        :param app_name: Django app name (used to locate app-level files).
        """
        ...
