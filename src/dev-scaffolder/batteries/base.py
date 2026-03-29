import os
import re
import sys
from abc import ABC, abstractmethod

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from typings.base import ExecutorResponseStatus


class BaseBattery(ABC):
    """
    Abstract base class for project batteries.

    A battery encapsulates an optional dependency that can be selectively
    applied to a scaffolded project. Each battery is responsible for
    installing its own packages and configuring the project's settings/files.

    Subclass this to create batteries for any framework (Django, FastAPI, etc.).
    """

    def __init__(self):
        self.console = Console()

    def _insert_app_re(self, content: str, new_app: str) -> str:
        """Append a new app entry at the end of the INSTALLED_APPS list."""
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

    def _insert_app_before(self, content: str, new_app: str, before_app: str) -> str:
        """
        Insert a new app entry immediately before an existing app in INSTALLED_APPS.

        Use this to ensure external/third-party apps are placed before custom
        project apps so that Django resolves them in the correct order.

        :param content: The full text of settings.py.
        :param new_app: The app label to insert (e.g. 'rest_framework').
        :param before_app: The existing app label to insert before (e.g. 'myapp').
        :return: Modified settings.py content.
        """
        return content.replace(
            f"    '{before_app}',",
            f"    '{new_app}',\n    '{before_app}',"
        )

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
        Apply configuration changes to the scaffolded project.

        :param project_path: Absolute path to the root of the project.
        :param project_name: Project package name (used to locate settings.py).
        :param app_name: App name (used to locate app-level files).
        """
        ...
