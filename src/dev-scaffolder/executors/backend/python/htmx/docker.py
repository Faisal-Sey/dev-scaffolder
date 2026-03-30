import argparse
import os
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
from constants.backend.python.base import (
    DJANGO_DOCKERFILE,
    DJANGO_DOCKER_COMPOSE,
    DJANGO_DOCKERIGNORE,
    DJANGO_DOCKER_ENV,
)
from utils.base import get_venv_python_executor


class HtmxDockerExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django + HTMX project with Docker support.

    Generates:
      - Dockerfile          (python:3.11-slim, installs requirements, exposes 8000)
      - docker-compose.yml  (web + postgres services)
      - .dockerignore
      - .env

    Accepts optional batteries that are applied after the base project and
    Docker files are created.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # Docker file writers
    # ------------------------------------------------------------------

    def _write_dockerfile(self, project_path: str) -> None:
        with open(os.path.join(project_path, 'Dockerfile'), 'w', encoding='utf-8') as f:
            f.write(DJANGO_DOCKERFILE)

    def _write_docker_compose(self, project_path: str) -> None:
        with open(os.path.join(project_path, 'docker-compose.yml'), 'w', encoding='utf-8') as f:
            f.write(DJANGO_DOCKER_COMPOSE)

    def _write_dockerignore(self, project_path: str) -> None:
        with open(os.path.join(project_path, '.dockerignore'), 'w', encoding='utf-8') as f:
            f.write(DJANGO_DOCKERIGNORE)

    def _write_env(self, project_path: str) -> None:
        with open(os.path.join(project_path, '.env'), 'w', encoding='utf-8') as f:
            f.write(DJANGO_DOCKER_ENV)

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django + HTMX project and adds Docker configuration files.

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

        self._update_status('[bold blue]Writing Dockerfile...[/bold blue]')
        self._write_dockerfile(project_path)

        self._update_status('[bold blue]Writing docker-compose.yml...[/bold blue]')
        self._write_docker_compose(project_path)

        self._update_status('[bold blue]Writing .dockerignore...[/bold blue]')
        self._write_dockerignore(project_path)

        self._update_status('[bold blue]Writing .env...[/bold blue]')
        self._write_env(project_path)

        venv_python_executor = get_venv_python_executor()

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
            f"[bold green]Django + HTMX + Docker project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Django + HTMX project with Docker support, scaffolded with dev-scaffolder.\n\n'
            '## Run with Docker\n\n'
            '> **Prerequisites:** Docker Desktop must be installed and running before executing any Docker commands.\n'
            '> If you see an error like `unable to get image` or `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`,\n'
            '> open Docker Desktop and wait for it to finish starting up, then try again.\n\n'
            '```bash\n'
            'docker compose up --build\n'
            '```\n\n'
            'Open http://localhost:8000 in your browser.\n\n'
            '### Environment\n\n'
            'Copy the example env file and set your values before starting:\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            '```\n\n'
            '### Apply migrations\n\n'
            '```bash\n'
            'docker compose exec web python manage.py migrate\n'
            '```\n\n'
            '### Create a superuser\n\n'
            '```bash\n'
            'docker compose exec web python manage.py createsuperuser\n'
            '```\n\n'
            '---\n\n'
            '## Run without Docker\n\n'
            '```bash\n'
            'python -m venv venv\n'
            'source venv/bin/activate       # macOS / Linux\n'
            'venv\\Scripts\\activate          # Windows\n\n'
            'pip install -r requirements.txt\n'
            'python manage.py migrate\n'
            'python manage.py runserver\n'
            '```\n'
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'test') or 'test'
        directory_name = kwargs.get('directory_name', '') or project_name
        app_name = kwargs.get('app_name', '') or 'core'

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
        parser.add_argument('--app_name', type=str, default='',
                            help='Name of the Django app (optional)')
        parser.add_argument('--batteries', type=str, default='',
                            help='Comma-separated batteries to apply, e.g. "PostgreSQL,Whitenoise"')
        return parser


def generate_htmx_docker_template(**kwargs) -> ExecutorResponseStatus:
    return HtmxDockerExecutor().run(**kwargs)


if __name__ == '__main__':
    args = HtmxDockerExecutor.build_arg_parser().parse_args()
    HtmxDockerExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
