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
    DjangoOfficialTemplateResponse,
    ExecutorResponseStatus,
)
from constants.backend.python.htmx.base import (
    HTMX_BASE_HTML,
    HTMX_INDEX_HTML,
    HTMX_VIEWS_PY,
    HTMX_APP_URLS_PY,
)
from utils.base import get_venv_python_executor


class HtmxOfficialExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django + HTMX project.

    Creates a Django project with a configured app, HTMX-powered templates,
    and wired-up URL routing. Supports optional batteries.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        from utils.base import run_subprocess_command
        command = [venv_python_executor, '-m', 'pip', 'install', 'django']
        if not run_subprocess_command(command):
            self.console.print('[bold red]Failed to install django[/bold red]')
            return ExecutorResponseStatus(success=False)
        self.console.print('[bold green]Django installed successfully[/bold green]')
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def _insert_app_re(self, content: str, new_app: str) -> str:
        """Insert a new app entry into INSTALLED_APPS using regex."""
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'

        def insert_app(match):
            prefix = match.group(1)
            apps_content = match.group(2)
            suffix = match.group(3)

            apps_content = apps_content.rstrip()

            if apps_content.strip():
                if not apps_content.strip().endswith(','):
                    apps_content += ','
                new_content = f"{prefix}{apps_content}\n    '{new_app}',\n{suffix}"
            else:
                new_content = f"{prefix}\n    '{new_app}',\n{suffix}"

            return new_content

        return re.sub(pattern, insert_app, content, flags=re.DOTALL)

    def _configure_installed_apps(self, settings_path: str, app_name: str) -> None:
        """Add app_name to INSTALLED_APPS in settings.py."""
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            modified = self._insert_app_re(content, app_name)
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(modified)
        except FileNotFoundError:
            self.console.print(
                f'[bold red]Settings file not found at {settings_path}[/bold red]'
            )

    def _configure_templates_dirs(self, settings_path: str) -> None:
        """Replace 'DIRS': [] with 'DIRS': [BASE_DIR / 'templates'] in settings.py."""
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            modified = content.replace(
                "'DIRS': []",
                "'DIRS': [BASE_DIR / 'templates']"
            )
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(modified)
        except FileNotFoundError:
            self.console.print(
                f'[bold red]Settings file not found at {settings_path}[/bold red]'
            )

    def _wire_app_urls(self, project_path: str, project_name: str, app_name: str) -> None:
        """Wire app URLs into the project urls.py at root path ''."""
        project_urls_path = os.path.join(project_path, project_name, 'urls.py')
        try:
            with open(project_urls_path, 'r', encoding='utf-8') as f:
                content = f.read()

            modified = content.replace(
                'from django.urls import path',
                'from django.urls import path, include'
            )
            modified = modified.replace(
                'urlpatterns = [\n',
                (
                    "urlpatterns = [\n"
                    f"    path('', include('{app_name}.urls')),\n"
                )
            )

            with open(project_urls_path, 'w', encoding='utf-8') as f:
                f.write(modified)
        except FileNotFoundError:
            self.console.print(
                f'[bold red]Project urls.py not found at {project_urls_path}[/bold red]'
            )

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django + HTMX project.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        app_name = kwargs['app_name']

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

        if response.message == 'APP_CREATION_FAILED':
            self.console.print('[bold red]App creation failed — cannot configure HTMX app[/bold red]')
            return ExecutorResponseStatus(success=False)

        project_path = response.path
        settings_path = os.path.join(project_path, project_name, 'settings.py')

        self._update_status('[bold blue]Configuring INSTALLED_APPS...[/bold blue]')
        self._configure_installed_apps(settings_path, app_name)

        self._update_status('[bold blue]Configuring TEMPLATES DIRS...[/bold blue]')
        self._configure_templates_dirs(settings_path)

        self._update_status('[bold blue]Wiring app URLs...[/bold blue]')
        self._wire_app_urls(project_path, project_name, app_name)

        self._update_status('[bold blue]Creating templates directory...[/bold blue]')
        templates_dir = os.path.join(project_path, 'templates')
        os.makedirs(templates_dir, exist_ok=True)

        self._update_status('[bold blue]Writing templates/base.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_BASE_HTML.format(project_name=project_name))

        self._update_status('[bold blue]Writing templates/index.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_INDEX_HTML.format(project_name=project_name))

        self._update_status('[bold blue]Writing views.py...[/bold blue]')
        with open(os.path.join(project_path, app_name, 'views.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_VIEWS_PY)

        self._update_status('[bold blue]Writing app urls.py...[/bold blue]')
        with open(os.path.join(project_path, app_name, 'urls.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_APP_URLS_PY)

        venv_python_executor = get_venv_python_executor()

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f'[bold blue]Applying {battery_name}...[/bold blue]')
            install_response = battery.install(venv_python_executor)
            if not install_response.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, app_name)

        self._update_status('[bold blue]Updating requirements.txt...[/bold blue]')
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name, app_name=app_name)

        self.console.print(
            f"[bold green]Django + HTMX project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Django + HTMX project scaffolded with dev-scaffolder.\n\n'
            '## Requirements\n\n'
            '- Python 3.8+\n\n'
            '## Setup\n\n'
            '```bash\n'
            'python -m venv venv\n'
            'source venv/bin/activate       # macOS / Linux\n'
            'venv\\Scripts\\activate          # Windows\n\n'
            'pip install -r requirements.txt\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'python manage.py migrate\n'
            'python manage.py runserver\n'
            '```\n\n'
            'Open http://localhost:8000 in your browser.\n'
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> DjangoOfficialTemplateResponse:
        """
        Generates the Django + HTMX project template.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app.
            - batteries (str): Comma-separated battery names.
        :return: DjangoOfficialTemplateResponse with success status and output path.
        :rtype: DjangoOfficialTemplateResponse
        """
        project_name = kwargs.get('project_name', 'test') or 'test'
        directory_name = kwargs.get('directory_name', '') or project_name
        app_name = kwargs.get('app_name', '') or 'core'

        batteries_arg = kwargs.get('batteries', '') or ''
        if batteries_arg and not self.batteries:
            self.batteries = parse_batteries(batteries_arg)

        project_path = os.path.join(self.current_folder, directory_name)

        creation_response = self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
        )

        return DjangoOfficialTemplateResponse(
            success=creation_response.success,
            message=creation_response.message,
            path=project_path,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject',
                            help='Name of the Django project')
        parser.add_argument('--directory_name', type=str, default='myproject',
                            help='Name of the project directory')
        parser.add_argument('--app_name', type=str, default='core',
                            help='Name of the Django app')
        parser.add_argument('--batteries', type=str, default='',
                            help='Comma-separated batteries to apply, e.g. "PostgreSQL,Whitenoise"')
        return parser


def generate_htmx_official_template(**kwargs) -> DjangoOfficialTemplateResponse:
    return HtmxOfficialExecutor().run(**kwargs)


if __name__ == '__main__':
    args = HtmxOfficialExecutor.build_arg_parser().parse_args()
    HtmxOfficialExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        app_name=args.app_name,
        batteries=args.batteries,
    )
