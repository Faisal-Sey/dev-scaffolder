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
    DjangoOfficialTemplateResponse,
    ExecutorResponseStatus,
)
from constants.backend.python.htmx.base import (
    HTMX_TAILWIND_BASE_HTML,
    HTMX_TAILWIND_INDEX_HTML,
)
from utils.base import get_venv_python_executor


class HtmxTailwindCssExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django + HTMX + Tailwind CSS project.

    Delegates base project setup to HtmxOfficialExecutor, then overwrites
    the templates with Tailwind CSS-styled versions (via CDN). Supports
    optional batteries.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django + HTMX + Tailwind CSS project.

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

        self._update_status(f"[bold blue]Scaffolding Django + HTMX base project '{project_name}'...[/bold blue]")
        response = htmx_executor.generate(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
            batteries='',
        )

        if not response.success:
            return ExecutorResponseStatus(success=False)

        project_path = os.path.join(self.current_folder, directory_name)
        templates_dir = os.path.join(project_path, 'templates')

        self._update_status('[bold blue]Writing Tailwind CSS base.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_TAILWIND_BASE_HTML.format(project_name=project_name))

        self._update_status('[bold blue]Writing Tailwind CSS index.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_TAILWIND_INDEX_HTML.format(project_name=project_name))

        venv_python_executor = get_venv_python_executor()

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f'[bold blue]Applying {battery_name}...[/bold blue]')
            install_response = battery.install(venv_python_executor)
            if not install_response.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, app_name)

        django_executor = DjangoOfficialExecutor()
        self._update_status('[bold blue]Updating requirements.txt...[/bold blue]')
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name, app_name=app_name)

        self.console.print(
            f"[bold green]Django + HTMX + Tailwind CSS project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Django + HTMX + Tailwind CSS project scaffolded with dev-scaffolder.\n\n'
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
            'Open http://localhost:8000 in your browser.\n\n'
            '## Stack\n\n'
            '- **Django** — server-side framework\n'
            '- **HTMX** — HTML-over-the-wire for dynamic content (CDN)\n'
            '- **Tailwind CSS** — utility-first CSS framework (CDN)\n'
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> DjangoOfficialTemplateResponse:
        """
        Generates the Django + HTMX + Tailwind CSS project template.

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


def generate_htmx_tailwind_css_template(**kwargs) -> DjangoOfficialTemplateResponse:
    return HtmxTailwindCssExecutor().run(**kwargs)


if __name__ == '__main__':
    args = HtmxTailwindCssExecutor.build_arg_parser().parse_args()
    HtmxTailwindCssExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        app_name=args.app_name,
        batteries=args.batteries,
    )
