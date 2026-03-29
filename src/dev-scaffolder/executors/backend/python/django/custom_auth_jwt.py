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
    DJANGO_CUSTOM_AUTH_MODEL,
    DJANGO_CUSTOM_AUTH_ADMIN,
    DJANGO_CUSTOM_AUTH_FORMS,
    DJANGO_JWT_DRF_SETTINGS,
    DJANGO_JWT_CBV_VIEWS,
    DJANGO_JWT_CBV_URL_CONFIG,
    DJANGO_JWT_FBV_VIEWS,
    DJANGO_JWT_FBV_URL_CONFIG,
)
from utils.base import run_subprocess_command, get_venv_python_executor


class DjangoCustomAuthJwtExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project with JWT-based authentication.

    Installs djangorestframework and djangorestframework-simplejwt, configures
    JWT authentication as the default DRF backend, and generates auth API
    endpoints (register, login, logout, token refresh, profile, forgot/reset
    password) in either class-based or function-based view style.

    Endpoints generated:
      POST  /<app>/register/
      POST  /<app>/login/
      POST  /<app>/logout/           (blacklists refresh token)
      POST  /<app>/token/refresh/    (simplejwt built-in)
      GET   /<app>/profile/
      PUT   /<app>/profile/
      POST  /<app>/forgot-password/
      POST  /<app>/reset-password/
    """

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['djangorestframework', 'djangorestframework-simplejwt']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f"[bold red]Failed to install {package}[/bold red]")
                return ExecutorResponseStatus(success=False)
            self.console.print(f"[bold green]{package} installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    def _insert_app_re(self, content: str, new_app: str) -> str:
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'

        def insert_app(match):
            prefix = match.group(1)
            apps_content = match.group(2).rstrip()
            suffix = match.group(3)
            if apps_content.strip() and not apps_content.strip().endswith(','):
                apps_content += ','
            return f"{prefix}{apps_content}\n    '{new_app}',\n{suffix}"

        return re.sub(pattern, insert_app, content, flags=re.DOTALL)

    def _insert_app_before(self, content: str, new_app: str, before_app: str) -> str:
        return content.replace(
            f"    '{before_app}',",
            f"    '{new_app}',\n    '{before_app}',"
        )

    def _configure_installed_apps(self, settings_path: str, app_name: str) -> None:
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            # Add auth app first, then insert third-party apps before it
            content = self._insert_app_re(content, app_name)
            content = self._insert_app_before(content, 'rest_framework', app_name)
            content = self._insert_app_before(content, 'rest_framework_simplejwt.token_blacklist', app_name)
            with open(settings_path, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

    def _append_jwt_settings(self, settings_path: str) -> None:
        try:
            with open(settings_path, 'a') as f:
                f.write(DJANGO_JWT_DRF_SETTINGS)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

    def _set_auth_user_model(self, settings_path: str, app_name: str) -> None:
        try:
            with open(settings_path, 'a') as f:
                f.write(f"\n\nAUTH_USER_MODEL = '{app_name}.User'\n")
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

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

    # ------------------------------------------------------------------
    # App file writers
    # ------------------------------------------------------------------

    def _write_models_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'models.py'), 'w') as f:
            f.write(DJANGO_CUSTOM_AUTH_MODEL)

    def _write_admin_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'admin.py'), 'w') as f:
            f.write(DJANGO_CUSTOM_AUTH_ADMIN)

    def _write_forms_py(self, app_path: str) -> None:
        with open(os.path.join(app_path, 'forms.py'), 'w') as f:
            f.write(DJANGO_CUSTOM_AUTH_FORMS)

    def _write_views_py(self, app_path: str, use_cbv: bool) -> None:
        content = DJANGO_JWT_CBV_VIEWS if use_cbv else DJANGO_JWT_FBV_VIEWS
        with open(os.path.join(app_path, 'views.py'), 'w') as f:
            f.write(content)

    def _write_urls_py(self, app_path: str, use_cbv: bool) -> None:
        content = DJANGO_JWT_CBV_URL_CONFIG if use_cbv else DJANGO_JWT_FBV_URL_CONFIG
        with open(os.path.join(app_path, 'urls.py'), 'w') as f:
            f.write(content)

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django project with JWT auth and DRF.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the auth app (e.g. 'users').
            - view_type (str): 'Class Based' or 'Function Based'.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs["project_name"]
        directory_name = kwargs["directory_name"]
        app_name = kwargs["app_name"]
        use_cbv = kwargs.get("view_type", "Class Based").strip().lower() == "class based"

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
            self.console.print("[bold red]App creation failed — cannot configure JWT auth[/bold red]")
            return ExecutorResponseStatus(success=False)

        project_path = response.path
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        app_path = os.path.join(project_path, app_name)
        view_label = "class-based" if use_cbv else "function-based"

        self._update_status("[bold blue]Installing DRF and simplejwt...[/bold blue]")
        venv_python_executor = get_venv_python_executor()
        install_response = self.install_dependencies(venv_python_executor)
        if not install_response.success:
            return ExecutorResponseStatus(success=False)

        self._update_status("[bold blue]Configuring INSTALLED_APPS...[/bold blue]")
        self._configure_installed_apps(settings_path, app_name)

        self._update_status("[bold blue]Appending JWT and DRF settings...[/bold blue]")
        self._append_jwt_settings(settings_path)

        self._update_status("[bold blue]Setting AUTH_USER_MODEL...[/bold blue]")
        self._set_auth_user_model(settings_path, app_name)

        self._update_status("[bold blue]Writing custom User model...[/bold blue]")
        self._write_models_py(app_path)

        self._update_status("[bold blue]Writing admin registration...[/bold blue]")
        self._write_admin_py(app_path)

        self._update_status("[bold blue]Writing auth forms...[/bold blue]")
        self._write_forms_py(app_path)

        self._update_status(f"[bold blue]Writing {view_label} JWT views...[/bold blue]")
        self._write_views_py(app_path, use_cbv)

        self._update_status(f"[bold blue]Writing {view_label} JWT URLs...[/bold blue]")
        self._write_urls_py(app_path, use_cbv)

        self._update_status("[bold blue]Wiring app URLs into project...[/bold blue]")
        self._integrate_app_url_into_project(project_path, project_name, app_name)

        self._update_status("[bold blue]Updating requirements.txt...[/bold blue]")
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self.console.print(
            f"[bold green]Django JWT auth ({view_label}) project "
            f"'{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        project_name = kwargs.get("project_name", "test") or "test"
        directory_name = kwargs.get("directory_name", "") or project_name
        app_name = kwargs.get("app_name", "users") or "users"
        view_type = kwargs.get("view_type", "Class Based") or "Class Based"

        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
            view_type=view_type,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject')
        parser.add_argument('--directory_name', type=str, default='myproject')
        parser.add_argument('--app_name', type=str, default='users')
        parser.add_argument('--view_type', type=str, default='Class Based',
                            help='View style: "Class Based" or "Function Based"')
        return parser


def generate_django_custom_auth_jwt_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoCustomAuthJwtExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoCustomAuthJwtExecutor.build_arg_parser().parse_args()
    DjangoCustomAuthJwtExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
        view_type=args.view_type,
    )
