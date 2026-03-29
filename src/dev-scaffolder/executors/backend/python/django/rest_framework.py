import argparse
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from executors.backend.python.django.batteries.rest_framework import RestFrameworkBattery
from executors.backend.python.django.batteries.cors_headers import CorsHeadersBattery
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
)
from utils.base import get_venv_python_executor


class DjangoRestFrameworkExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project with Django REST Framework and
    django-cors-headers pre-configured.

    Batteries applied:
      - RestFrameworkBattery: installs DRF, configures INSTALLED_APPS/settings,
        and generates a starter serializer, APIView, and URL config.
      - CorsHeadersBattery: installs django-cors-headers and configures middleware
        and CORS settings.
    """

    def __init__(self):
        super().__init__()
        self.batteries = [RestFrameworkBattery(), CorsHeadersBattery()]

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        # Delegated to batteries
        return ExecutorResponseStatus(success=True)

    def _integrate_app_url_into_project(
            self, project_path: str, project_name: str, app_name: str
    ) -> None:
        project_urls_path = os.path.join(project_path, project_name, 'urls.py')
        try:
            with open(project_urls_path, 'r') as f:
                content = f.read()
            modified = content.replace(
                'urlpatterns = [\n',
                f"urlpatterns = [\n    path('{app_name}/', include('{app_name}.urls')),\n"
            )
            modified = modified.replace(
                "from django.urls import path",
                "from django.urls import path, include"
            )
            with open(project_urls_path, 'w') as f:
                f.write(modified)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {project_urls_path}[/bold red]")

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django project, then applies RestFrameworkBattery and
        CorsHeadersBattery in sequence.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app to create and configure.
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

        if response.message == "APP_CREATION_FAILED" and app_name:
            self.console.print("[bold red]App creation failed — cannot configure REST Framework[/bold red]")
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

        if app_name:
            self._update_status("[bold blue]Wiring app URLs into project...[/bold blue]")
            self._integrate_app_url_into_project(project_path, project_name, app_name)

        self._update_status("[bold blue]Updating requirements.txt...[/bold blue]")
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self.console.print(
            f"[bold green]Django REST Framework project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        """
        Internal implementation for generating the Django REST Framework template.

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
        app_name = kwargs.get("app_name", "api") or "api"

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
        parser.add_argument('--app_name', type=str, default='api',
                            help='Name of the Django app')
        return parser


# Module-level shim so existing callers using generate_django_rest_framework_template() still work
def generate_django_rest_framework_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoRestFrameworkExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoRestFrameworkExecutor.build_arg_parser().parse_args()
    DjangoRestFrameworkExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
    )
