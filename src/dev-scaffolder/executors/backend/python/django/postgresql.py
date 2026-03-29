import argparse
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from executors.backend.python.django.batteries.postgresql import PostgreSQLBattery
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
)
from utils.base import get_venv_python_executor


class DjangoPostgreSQLExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project configured to use PostgreSQL.

    Batteries applied:
      - PostgreSQLBattery: installs psycopg2-binary and python-dotenv, replaces
        the default SQLite DATABASES config with a PostgreSQL config driven by
        environment variables, and generates a .env.example file.
    """

    def __init__(self):
        super().__init__()
        self.batteries = [PostgreSQLBattery()]

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        # Delegated to batteries
        return ExecutorResponseStatus(success=True)

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django project and applies PostgreSQLBattery.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app to create.
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

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f"[bold blue]Applying {battery_name}...[/bold blue]")
            install_response = battery.install(venv_python_executor)
            if not install_response.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, app_name)

        self._update_status("[bold blue]Updating requirements.txt...[/bold blue]")
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self.console.print(
            f"[bold green]Django + PostgreSQL project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        """
        Internal implementation for generating the Django + PostgreSQL template.

        Resolves arguments and delegates to execute_creation_commands.
        Called by run(); do not call directly.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs.get("project_name", "test") or "test"
        directory_name = kwargs.get("directory_name", "") or project_name
        app_name = kwargs.get("app_name", "") or ""

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
        return parser


# Module-level shim for callers using generate_django_postgresql_template()
def generate_django_postgresql_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoPostgreSQLExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoPostgreSQLExecutor.build_arg_parser().parse_args()
    DjangoPostgreSQLExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
    )
