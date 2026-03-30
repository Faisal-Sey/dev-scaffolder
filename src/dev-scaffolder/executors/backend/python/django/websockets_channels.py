import argparse
import os
import re
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from batteries.base import BaseBattery
from batteries.registry import parse_batteries
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
)
from constants.backend.python.base import (
    DJANGO_CHANNELS_SETTINGS,
    DJANGO_CHANNELS_CONSUMER,
    DJANGO_CHANNELS_ROUTING,
)
from utils.base import run_subprocess_command, get_venv_python_executor


class DjangoWebSocketsChannelsExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project with WebSocket support via
    Django Channels and a Redis channel layer.

    Installs daphne, channels, and channels-redis. Configures the project to
    run under ASGI (Daphne), replaces asgi.py with a ProtocolTypeRouter, and
    generates a starter ChatConsumer with group broadcast support.

    Generated files:
      {project_name}/asgi.py      — ProtocolTypeRouter (http + websocket)
      {app_name}/consumers.py     — AsyncWebsocketConsumer (ChatConsumer)
      {app_name}/routing.py       — websocket_urlpatterns

    WebSocket endpoint:
      ws://localhost:8000/ws/chat/
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['daphne', 'channels', 'channels-redis']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f"[bold red]Failed to install {package}[/bold red]")
                return ExecutorResponseStatus(success=False)
            self.console.print(f"[bold green]{package} installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    def _insert_app_at_top(self, content: str, new_app: str) -> str:
        """Insert an app as the very first entry in INSTALLED_APPS."""
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'

        def insert_first(match):
            prefix = match.group(1)
            apps_content = match.group(2)
            suffix = match.group(3)
            apps_content = apps_content.lstrip('\n')
            return f"{prefix}\n    '{new_app}',\n{apps_content}{suffix}"

        return re.sub(pattern, insert_first, content, flags=re.DOTALL)

    def _insert_app_after(self, content: str, new_app: str, after_app: str) -> str:
        """Insert a new app entry immediately after an existing app in INSTALLED_APPS."""
        return content.replace(
            f"    '{after_app}',",
            f"    '{after_app}',\n    '{new_app}',"
        )

    def _configure_installed_apps(self, settings_path: str, app_name: str) -> None:
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            # daphne must be first to override runserver with ASGI
            content = self._insert_app_at_top(content, 'daphne')
            content = self._insert_app_after(content, 'channels', 'daphne')
            if app_name:
                content = self._insert_app_after(content, app_name, 'channels')
            with open(settings_path, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

    def _set_asgi_application(self, settings_path: str, project_name: str) -> None:
        """Replace WSGI_APPLICATION with ASGI_APPLICATION."""
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            content = re.sub(
                r"WSGI_APPLICATION\s*=\s*['\"].*?['\"]",
                f"ASGI_APPLICATION = '{project_name}.asgi.application'",
                content,
            )
            with open(settings_path, 'w') as f:
                f.write(content)
            with open(settings_path, 'a') as f:
                f.write(DJANGO_CHANNELS_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

    # ------------------------------------------------------------------
    # File writers
    # ------------------------------------------------------------------

    def _write_asgi_py(self, project_path: str, project_name: str, app_name: str) -> None:
        content = (
            "import os\n"
            "from django.core.asgi import get_asgi_application\n"
            "from channels.routing import ProtocolTypeRouter, URLRouter\n"
            "from channels.auth import AuthMiddlewareStack\n"
            f"import {app_name}.routing\n\n"
            f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')\n\n"
            "application = ProtocolTypeRouter({\n"
            "    'http': get_asgi_application(),\n"
            "    'websocket': AuthMiddlewareStack(\n"
            "        URLRouter(\n"
            f"            {app_name}.routing.websocket_urlpatterns\n"
            "        )\n"
            "    ),\n"
            "})\n"
        )
        with open(os.path.join(project_path, project_name, 'asgi.py'), 'w') as f:
            f.write(content)

    def _write_consumers_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'consumers.py'), 'w') as f:
            f.write(DJANGO_CHANNELS_CONSUMER)

    def _write_routing_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'routing.py'), 'w') as f:
            f.write(DJANGO_CHANNELS_ROUTING)

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django project with WebSocket support via Django Channels.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app for consumers/routing.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs["project_name"]
        directory_name = kwargs["directory_name"]
        app_name = kwargs["app_name"]

        django_executor = DjangoOfficialExecutor()
        django_executor._status = self._status

        self._update_status(f"[bold blue]Scaffolding Django project '{project_name}'...[/bold blue]")
        response = django_executor.generate(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
        )

        if not response.success:
            return ExecutorResponseStatus(success=False)

        if response.message == "APP_CREATION_FAILED":
            self.console.print("[bold red]App creation failed — consumers and routing require an app[/bold red]")
            return ExecutorResponseStatus(success=False)

        project_path = response.path
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        app_path = os.path.join(project_path, app_name)

        self._update_status("[bold blue]Installing daphne, channels, channels-redis...[/bold blue]")
        venv_python_executor = get_venv_python_executor()
        install_response = self.install_dependencies(venv_python_executor)
        if not install_response.success:
            return ExecutorResponseStatus(success=False)

        self._update_status("[bold blue]Configuring INSTALLED_APPS...[/bold blue]")
        self._configure_installed_apps(settings_path, app_name)

        self._update_status("[bold blue]Setting ASGI_APPLICATION and channel layer...[/bold blue]")
        self._set_asgi_application(settings_path, project_name)

        self._update_status("[bold blue]Writing asgi.py...[/bold blue]")
        self._write_asgi_py(project_path, project_name, app_name)

        self._update_status("[bold blue]Writing consumers.py...[/bold blue]")
        self._write_consumers_py(app_path)

        self._update_status("[bold blue]Writing routing.py...[/bold blue]")
        self._write_routing_py(app_path)

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f"[bold blue]Applying {battery_name}...[/bold blue]")
            install_response = battery.install(venv_python_executor)
            if not install_response.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, app_name)

        self._update_status("[bold blue]Updating requirements.txt...[/bold blue]")
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self._update_status("[bold blue]Writing README.md...[/bold blue]")
        self._write_readme(project_path, project_name=project_name, app_name=app_name)

        self.console.print(
            f"[bold green]Django Channels project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get("project_name", "project")
        app_name = kwargs.get("app_name", "chat")
        return (
            f"# {project_name}\n\n"
            "A Django project with WebSocket support via Django Channels, "
            "scaffolded with dev-scaffolder.\n\n"
            "## Requirements\n\n"
            "- Python 3.8+\n"
            "- Redis (used as the channel layer backend)\n\n"
            "## Setup\n\n"
            "```bash\n"
            "python -m venv venv\n"
            "source venv/bin/activate       # macOS / Linux\n"
            "venv\\Scripts\\activate          # Windows\n\n"
            "pip install -r requirements.txt\n"
            "```\n\n"
            "## Start Redis\n\n"
            "Redis must be running before starting the server:\n\n"
            "```bash\n"
            "# macOS (Homebrew)\n"
            "brew services start redis\n\n"
            "# Linux\n"
            "sudo systemctl start redis\n\n"
            "# Docker\n"
            "docker run -p 6379:6379 redis:7\n"
            "```\n\n"
            "## Run\n\n"
            "```bash\n"
            "python manage.py migrate\n"
            "python manage.py runserver\n"
            "```\n\n"
            "Daphne serves the app over ASGI automatically when `daphne` is first in `INSTALLED_APPS`.\n\n"
            "## WebSocket Endpoint\n\n"
            f"Connect to `ws://localhost:8000/ws/chat/` to interact with the `ChatConsumer`.\n\n"
            "The consumer broadcasts any received message to all clients in the `chat` group.\n\n"
            "## Project Structure\n\n"
            "```\n"
            f"{app_name}/\n"
            "  consumers.py   — AsyncWebsocketConsumer (ChatConsumer)\n"
            "  routing.py     — websocket_urlpatterns\n"
            f"{project_name}/\n"
            "  asgi.py        — ProtocolTypeRouter (http + websocket)\n"
            "```\n"
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        project_name = kwargs.get("project_name", "test") or "test"
        directory_name = kwargs.get("directory_name", "") or project_name
        app_name = kwargs.get("app_name", "chat") or "chat"

        batteries_arg = kwargs.get("batteries", "") or ""
        if batteries_arg and not self.batteries:
            self.batteries = parse_batteries(batteries_arg)

        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject',
                            help='Name of the Django project')
        parser.add_argument('--directory_name', type=str, default='myproject',
                            help='Name of the Django project directory')
        parser.add_argument('--app_name', type=str, default='chat',
                            help='Name of the app for consumers and routing')
        parser.add_argument('--batteries', type=str, default='',
                            help='Comma-separated extra batteries, e.g. "PostgreSQL,Celery"')
        return parser


def generate_django_websockets_channels_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoWebSocketsChannelsExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoWebSocketsChannelsExecutor.build_arg_parser().parse_args()
    DjangoWebSocketsChannelsExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
