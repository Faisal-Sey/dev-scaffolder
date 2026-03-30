import argparse
import os
import re
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from executors.backend.python.htmx.official import HtmxOfficialExecutor
from batteries.base import BaseBattery
from batteries.registry import parse_batteries
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
)
from utils.base import run_subprocess_command, get_venv_python_executor

HTMX_WS_CHANNEL_LAYERS = (
    "\n\nCHANNEL_LAYERS = {\n"
    '    "default": {\n'
    '        "BACKEND": "channels_redis.core.RedisChannelLayer",\n'
    '        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},\n'
    "    },\n"
    "}\n"
)

HTMX_WS_BASE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{project_name}{{% endblock %}}</title>
    <script src="https://unpkg.com/htmx.org@2.0.3"></script>
    <script src="https://unpkg.com/htmx-ext-ws@2.0.1/ws.js"></script>
    {{% block extra_head %}}{{% endblock %}}
    <style>
        body {{ font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }}
        #messages {{ border: 1px solid #ddd; border-radius: 4px; padding: 12px; min-height: 200px; margin-bottom: 12px; }}
        .message {{ margin: 4px 0; }}
        input[type=text] {{ width: 80%; padding: 8px; }}
        button {{ padding: 8px 16px; }}
    </style>
</head>
<body>
    {{% block content %}}{{% endblock %}}
</body>
</html>
"""

HTMX_WS_INDEX_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Chat \u2014 {project_name}{{% endblock %}}
{{% block content %}}
<h1>{project_name} \u2014 Live Chat</h1>
<div hx-ext="ws" ws-connect="/ws/chat/">
    <div id="messages"></div>
    <form ws-send>
        <input type="text" name="message" placeholder="Type a message..." autocomplete="off">
        <button type="submit">Send</button>
    </form>
</div>
{{% endblock %}}
"""

HTMX_WS_CONSUMERS_PY = """\
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat'
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'chat_message', 'message': message},
        )

    async def chat_message(self, event):
        message = event['message']
        # Send an HTML fragment that HTMX will swap into the DOM
        await self.send(text_data=(
            f'<div id="messages" hx-swap-oob="beforeend">'
            f'<p class="message">{message}</p>'
            f'</div>'
        ))
"""

HTMX_WS_ROUTING_PY = """\
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]
"""


class HtmxWebSocketsExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django + HTMX project with WebSocket support.

    HTMX WebSockets use the HTMX WebSocket extension on the frontend and
    Django Channels on the backend. The backend sends HTML fragments back
    over the WebSocket connection.

    Installs daphne, channels, and channels-redis. Configures the project to
    run under ASGI (Daphne), replaces asgi.py with a ProtocolTypeRouter, and
    generates a ChatConsumer that returns HTML fragments.

    Generated files:
      {project_name}/asgi.py      — ProtocolTypeRouter (http + websocket)
      {app_name}/consumers.py     — AsyncWebsocketConsumer (ChatConsumer)
      {app_name}/routing.py       — websocket_urlpatterns
      templates/base.html         — HTMX + HTMX WS extension CDN
      templates/index.html        — Chat UI using hx-ext="ws"

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
                self.console.print(f'[bold red]Failed to install {package}[/bold red]')
                return ExecutorResponseStatus(success=False)
            self.console.print(f'[bold green]{package} installed successfully[/bold green]')
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
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # daphne must be first to override runserver with ASGI
            content = self._insert_app_at_top(content, 'daphne')
            content = self._insert_app_after(content, 'channels', 'daphne')
            if app_name:
                content = self._insert_app_after(content, app_name, 'channels')
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {settings_path}[/bold red]')

    def _set_asgi_application(self, settings_path: str, project_name: str) -> None:
        """Replace WSGI_APPLICATION with ASGI_APPLICATION and append channel layer config."""
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(
                r"WSGI_APPLICATION\s*=\s*['\"].*?['\"]",
                f"ASGI_APPLICATION = '{project_name}.asgi.application'",
                content,
            )
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(content)
            with open(settings_path, 'a') as f:
                f.write(HTMX_WS_CHANNEL_LAYERS)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {settings_path}[/bold red]')

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
            f.write(HTMX_WS_CONSUMERS_PY)

    def _write_routing_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'routing.py'), 'w') as f:
            f.write(HTMX_WS_ROUTING_PY)

    def _write_base_html(self, templates_dir: str, project_name: str) -> None:
        with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
            f.write(HTMX_WS_BASE_HTML.format(project_name=project_name))

    def _write_index_html(self, templates_dir: str, project_name: str) -> None:
        with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
            f.write(HTMX_WS_INDEX_HTML.format(project_name=project_name))

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django + HTMX project with WebSocket support via Django Channels.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app for consumers/routing.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        app_name = kwargs['app_name']

        htmx_executor = HtmxOfficialExecutor()
        htmx_executor._status = self._status

        self._update_status(f"[bold blue]Scaffolding Django + HTMX project '{project_name}'...[/bold blue]")
        response = htmx_executor.generate(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
        )

        if not response.success:
            return ExecutorResponseStatus(success=False)

        project_path = response.path
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        app_path = os.path.join(project_path, app_name)
        templates_dir = os.path.join(project_path, 'templates')

        self._update_status('[bold blue]Installing daphne, channels, channels-redis...[/bold blue]')
        venv_python_executor = get_venv_python_executor()
        install_response = self.install_dependencies(venv_python_executor)
        if not install_response.success:
            return ExecutorResponseStatus(success=False)

        self._update_status('[bold blue]Configuring INSTALLED_APPS...[/bold blue]')
        self._configure_installed_apps(settings_path, app_name)

        self._update_status('[bold blue]Setting ASGI_APPLICATION and channel layer...[/bold blue]')
        self._set_asgi_application(settings_path, project_name)

        self._update_status('[bold blue]Writing asgi.py...[/bold blue]')
        self._write_asgi_py(project_path, project_name, app_name)

        self._update_status('[bold blue]Writing consumers.py...[/bold blue]')
        self._write_consumers_py(app_path)

        self._update_status('[bold blue]Writing routing.py...[/bold blue]')
        self._write_routing_py(app_path)

        self._update_status('[bold blue]Writing templates/base.html (with HTMX WS extension)...[/bold blue]')
        self._write_base_html(templates_dir, project_name)

        self._update_status('[bold blue]Writing templates/index.html (chat UI)...[/bold blue]')
        self._write_index_html(templates_dir, project_name)

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f'[bold blue]Applying {battery_name}...[/bold blue]')
            install_response = battery.install(venv_python_executor)
            if not install_response.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, app_name)

        self._update_status('[bold blue]Updating requirements.txt...[/bold blue]')
        django_executor = DjangoOfficialExecutor()
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name, app_name=app_name)

        self.console.print(
            f"[bold green]Django + HTMX + WebSockets project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        app_name = kwargs.get('app_name', 'chat')
        return (
            f'# {project_name}\n\n'
            'A Django + HTMX project with WebSocket support via Django Channels, '
            'scaffolded with dev-scaffolder.\n\n'
            'The HTMX WebSocket extension (`htmx-ext-ws`) is used on the frontend '
            'to connect to the Django Channels backend, which sends HTML fragments '
            'back over the WebSocket connection.\n\n'
            '## Requirements\n\n'
            '- Python 3.8+\n'
            '- Redis (used as the channel layer backend)\n\n'
            '## Setup\n\n'
            '```bash\n'
            'python -m venv venv\n'
            'source venv/bin/activate       # macOS / Linux\n'
            'venv\\Scripts\\activate          # Windows\n\n'
            'pip install -r requirements.txt\n'
            '```\n\n'
            '## Start Redis\n\n'
            'Redis must be running before starting the server:\n\n'
            '```bash\n'
            '# macOS (Homebrew)\n'
            'brew services start redis\n\n'
            '# Linux\n'
            'sudo systemctl start redis\n\n'
            '# Docker\n'
            'docker run -p 6379:6379 redis:7\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'python manage.py migrate\n'
            'python manage.py runserver\n'
            '```\n\n'
            'Daphne serves the app over ASGI automatically when `daphne` is first in `INSTALLED_APPS`.\n\n'
            '## WebSocket Endpoint\n\n'
            f'Connect to `ws://localhost:8000/ws/chat/` to use the live chat UI.\n\n'
            'The HTMX WS extension handles the connection via `hx-ext="ws"` and `ws-connect` attributes. '
            'The server responds with HTML fragments that HTMX swaps into the DOM.\n\n'
            '## Project Structure\n\n'
            '```\n'
            f'{app_name}/\n'
            '  consumers.py   — AsyncWebsocketConsumer (ChatConsumer, returns HTML fragments)\n'
            '  routing.py     — websocket_urlpatterns\n'
            f'{project_name}/\n'
            '  asgi.py        — ProtocolTypeRouter (http + websocket)\n'
            'templates/\n'
            '  base.html      — HTMX + htmx-ext-ws CDN included\n'
            '  index.html     — Chat UI with hx-ext="ws"\n'
            '```\n'
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'test') or 'test'
        directory_name = kwargs.get('directory_name', '') or project_name
        app_name = kwargs.get('app_name', '') or 'chat'

        batteries_arg = kwargs.get('batteries', '') or ''
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
                            help='Name of the app for consumers and routing (e.g. chat)')
        parser.add_argument('--batteries', type=str, default='',
                            help='Comma-separated batteries to apply, e.g. "PostgreSQL,Pytest"')
        return parser


def generate_htmx_websockets_template(**kwargs) -> ExecutorResponseStatus:
    return HtmxWebSocketsExecutor().run(**kwargs)


if __name__ == '__main__':
    args = HtmxWebSocketsExecutor.build_arg_parser().parse_args()
    HtmxWebSocketsExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
