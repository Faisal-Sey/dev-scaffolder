import argparse
import os
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from batteries.base import BaseBattery
from batteries.django import WhitenoiseBattery
from batteries.registry import parse_batteries
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
)
from constants.backend.python.base import DJANGO_SAMPLE_CSS
from utils.base import get_venv_python_executor


class DjangoStaticFilesExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project configured for static file serving
    via whitenoise.

    Always applies WhitenoiseBattery (installs whitenoise, wires middleware and
    INSTALLED_APPS, appends STATIC_ROOT / STATICFILES_DIRS / STATICFILES_STORAGE).

    Also creates a starter static directory layout:
      static/
        css/style.css
        js/
        images/

    Additional optional batteries (postgresql, rest_framework, etc.) can be
    passed in via the batteries prompt.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # Static directory helpers
    # ------------------------------------------------------------------

    def _create_static_dirs(self, project_path: str) -> None:
        for subdir in ['css', 'js', 'images']:
            os.makedirs(os.path.join(project_path, 'static', subdir), exist_ok=True)

    def _write_sample_css(self, project_path: str) -> None:
        css_path = os.path.join(project_path, 'static', 'css', 'style.css')
        with open(css_path, 'w') as f:
            f.write(DJANGO_SAMPLE_CSS)

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django project with whitenoise static file serving.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app (optional).
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

        project_path = response.path
        venv_python_executor = get_venv_python_executor()

        self._update_status("[bold blue]Installing and configuring whitenoise...[/bold blue]")
        whitenoise = WhitenoiseBattery()
        install_response = whitenoise.install(venv_python_executor)
        if not install_response.success:
            return ExecutorResponseStatus(success=False)
        whitenoise.configure(project_path, project_name, app_name)

        self._update_status("[bold blue]Creating static directory layout...[/bold blue]")
        self._create_static_dirs(project_path)
        self._write_sample_css(project_path)

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
            f"[bold green]Django static files project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get("project_name", "project")
        return (
            f"# {project_name}\n\n"
            "A Django project configured for static file serving with whitenoise, "
            "scaffolded with dev-scaffolder.\n\n"
            "## Requirements\n\n"
            "- Python 3.8+\n\n"
            "## Setup\n\n"
            "```bash\n"
            "python -m venv venv\n"
            "source venv/bin/activate       # macOS / Linux\n"
            "venv\\Scripts\\activate          # Windows\n\n"
            "pip install -r requirements.txt\n"
            "```\n\n"
            "## Run\n\n"
            "```bash\n"
            "python manage.py migrate\n"
            "python manage.py runserver\n"
            "```\n\n"
            "## Static Files\n\n"
            "Static files are served by [whitenoise](https://whitenoise.readthedocs.io/).\n\n"
            "Place your static assets in the `static/` directory:\n\n"
            "```\n"
            "static/\n"
            "  css/style.css\n"
            "  js/\n"
            "  images/\n"
            "```\n\n"
            "Before deploying, collect static files into `staticfiles/`:\n\n"
            "```bash\n"
            "python manage.py collectstatic\n"
            "```\n\n"
            "Whitenoise will then serve everything under `STATIC_ROOT` directly "
            "from the WSGI layer with no extra web server configuration needed.\n"
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        project_name = kwargs.get("project_name", "test") or "test"
        directory_name = kwargs.get("directory_name", "") or project_name
        app_name = kwargs.get("app_name", "") or ""

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
        parser.add_argument('--app_name', type=str, default='',
                            help='Name of the Django app (optional)')
        parser.add_argument('--batteries', type=str, default='',
                            help='Comma-separated extra batteries, e.g. "PostgreSQL,CORS Headers"')
        return parser


def generate_django_static_files_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoStaticFilesExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoStaticFilesExecutor.build_arg_parser().parse_args()
    DjangoStaticFilesExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
