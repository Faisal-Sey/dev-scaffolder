import argparse
import os
import re
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
)
from constants.backend.python.base import (
    DJANGO_CORS_SETTINGS,
    DJANGO_DRF_SETTINGS,
    DJANGO_DRF_SERIALIZER,
    DJANGO_DRF_VIEW,
    DJANGO_DRF_URL_CONFIG,
)
from utils.base import run_subprocess_command, get_venv_python_executor


class DjangoRestFrameworkExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project with Django REST Framework.

    Builds on DjangoOfficialExecutor by installing djangorestframework,
    adding it to INSTALLED_APPS, configuring DRF settings, and generating
    a starter serializer, APIView, and URL configuration in the app.
    """

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['djangorestframework', 'django-cors-headers']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f"[bold red]Failed to install {package}[/bold red]")
                return ExecutorResponseStatus(success=False)
            self.console.print(f"[bold green]{package} installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

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

    def _add_to_installed_apps(self, settings_path: str, app_name: str) -> None:
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            modified = self._insert_app_re(content, app_name)
            with open(settings_path, 'w') as f:
                f.write(modified)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

    def _insert_cors_middleware(self, content: str) -> str:
        """Insert CorsMiddleware before CommonMiddleware in the MIDDLEWARE list."""
        return content.replace(
            "    'django.middleware.common.CommonMiddleware',",
            "    'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.common.CommonMiddleware',"
        )

    def _append_drf_settings(self, settings_path: str) -> None:
        try:
            with open(settings_path, 'a') as f:
                f.write(DJANGO_DRF_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

    def _create_serializers_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'serializers.py'), 'w') as f:
            f.write(DJANGO_DRF_SERIALIZER)

    def _update_views_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'views.py'), 'w') as f:
            f.write(DJANGO_DRF_VIEW)

    def _create_app_urls_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'urls.py'), 'w') as f:
            f.write(DJANGO_DRF_URL_CONFIG)

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
        Scaffolds a Django project, installs DRF, and configures a starter API.

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
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        venv_python_executor = get_venv_python_executor()

        self._update_status("[bold blue]Installing Django REST Framework...[/bold blue]")
        install_response = self.install_dependencies(venv_python_executor)
        if not install_response.success:
            return ExecutorResponseStatus(success=False)

        self._update_status("[bold blue]Configuring INSTALLED_APPS, middleware, and DRF settings...[/bold blue]")
        if app_name:
            self._add_to_installed_apps(settings_path, app_name)
        self._add_to_installed_apps(settings_path, 'rest_framework')
        self._add_to_installed_apps(settings_path, 'corsheaders')
        self._append_drf_settings(settings_path)

        self._update_status("[bold blue]Configuring CORS...[/bold blue]")
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            content = self._insert_cors_middleware(content)
            with open(settings_path, 'w') as f:
                f.write(content)
            with open(settings_path, 'a') as f:
                f.write(DJANGO_CORS_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

        if app_name:
            app_path = os.path.join(project_path, app_name)
            self._update_status(
                f"[bold blue]Creating DRF serializer, view, and URLs in '{app_name}'...[/bold blue]"
            )
            self._create_serializers_py(app_path)
            self._update_views_py(app_path)
            self._create_app_urls_py(app_path)
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
