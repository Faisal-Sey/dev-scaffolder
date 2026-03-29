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
    DJANGO_CUSTOM_AUTH_CBV_VIEWS,
    DJANGO_CUSTOM_AUTH_CBV_URL_CONFIG,
    DJANGO_CUSTOM_AUTH_FBV_VIEWS,
    DJANGO_CUSTOM_AUTH_FBV_URL_CONFIG,
)
from utils.base import get_venv_python_executor


class DjangoCustomAuthApisExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project with a custom User model and
    JSON auth API endpoints (register, login, logout, profile).

    Supports two view styles selected at prompt time:
      - Class Based: uses Django's View with method_decorator
      - Function Based: uses plain functions with decorators

    Both styles use Django's built-in session auth and JsonResponse —
    no extra packages required.

    Endpoints generated:
      POST   /<app>/register/
      POST   /<app>/login/
      POST   /<app>/logout/
      GET    /<app>/profile/
      PUT    /<app>/profile/
    """

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        # Uses only Django built-ins — no extra packages needed.
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

    def _add_to_installed_apps(self, settings_path: str, app_name: str) -> None:
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            content = self._insert_app_re(content, app_name)
            with open(settings_path, 'w') as f:
                f.write(content)
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
        content = DJANGO_CUSTOM_AUTH_CBV_VIEWS if use_cbv else DJANGO_CUSTOM_AUTH_FBV_VIEWS
        with open(os.path.join(app_path, 'views.py'), 'w') as f:
            f.write(content)

    def _write_urls_py(self, app_path: str, use_cbv: bool) -> None:
        content = DJANGO_CUSTOM_AUTH_CBV_URL_CONFIG if use_cbv else DJANGO_CUSTOM_AUTH_FBV_URL_CONFIG
        with open(os.path.join(app_path, 'urls.py'), 'w') as f:
            f.write(content)

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django project with custom User model and auth API endpoints.

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
            self.console.print("[bold red]App creation failed — cannot configure auth APIs[/bold red]")
            return ExecutorResponseStatus(success=False)

        project_path = response.path
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        app_path = os.path.join(project_path, app_name)
        view_label = "class-based" if use_cbv else "function-based"

        self._update_status("[bold blue]Adding app to INSTALLED_APPS...[/bold blue]")
        self._add_to_installed_apps(settings_path, app_name)

        self._update_status("[bold blue]Setting AUTH_USER_MODEL...[/bold blue]")
        self._set_auth_user_model(settings_path, app_name)

        self._update_status("[bold blue]Writing custom User model...[/bold blue]")
        self._write_models_py(app_path)

        self._update_status("[bold blue]Writing admin registration...[/bold blue]")
        self._write_admin_py(app_path)

        self._update_status("[bold blue]Writing auth forms...[/bold blue]")
        self._write_forms_py(app_path)

        self._update_status(f"[bold blue]Writing {view_label} auth views...[/bold blue]")
        self._write_views_py(app_path, use_cbv)

        self._update_status(f"[bold blue]Writing {view_label} auth URLs...[/bold blue]")
        self._write_urls_py(app_path, use_cbv)

        self._update_status("[bold blue]Wiring app URLs into project...[/bold blue]")
        self._integrate_app_url_into_project(project_path, project_name, app_name)

        self._update_status("[bold blue]Updating requirements.txt...[/bold blue]")
        venv_python_executor = get_venv_python_executor()
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self._update_status("[bold blue]Writing README.md...[/bold blue]")
        self._write_readme(project_path, project_name=project_name, app_name=app_name, view_label=view_label)

        self.console.print(
            f"[bold green]Django custom auth APIs ({view_label}) project "
            f"'{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        """
        Internal implementation for generating the Django custom auth APIs template.

        Resolves arguments and delegates to execute_creation_commands.
        Called by run(); do not call directly.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the auth app.
            - view_type (str): 'Class Based' or 'Function Based'.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
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

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get("project_name", "project")
        app_name = kwargs.get("app_name", "users")
        view_label = kwargs.get("view_label", "class-based")
        return (
            f"# {project_name}\n\n"
            f"A Django project with session-based auth API endpoints ({view_label} views), "
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
            "## Database\n\n"
            "```bash\n"
            "python manage.py makemigrations\n"
            "python manage.py migrate\n"
            "```\n\n"
            "## Run\n\n"
            "```bash\n"
            "python manage.py runserver\n"
            "```\n\n"
            "## Auth API Endpoints\n\n"
            f"All endpoints are served under `/{app_name}/`.\n\n"
            "| Method | URL | Description |\n"
            "|--------|-----|-------------|\n"
            f"| POST | `/{app_name}/register/` | Register a new user |\n"
            f"| POST | `/{app_name}/login/` | Log in (session cookie) |\n"
            f"| POST | `/{app_name}/logout/` | Log out |\n"
            f"| GET | `/{app_name}/profile/` | Get profile (auth required) |\n"
            f"| PUT | `/{app_name}/profile/` | Update profile (auth required) |\n"
            f"| POST | `/{app_name}/forgot-password/` | Request password reset |\n"
            f"| POST | `/{app_name}/reset-password/` | Reset password with token |\n\n"
            "Authentication uses Django's built-in session cookies — no extra packages required.\n"
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject',
                            help='Name of the Django project')
        parser.add_argument('--directory_name', type=str, default='myproject',
                            help='Name of the Django project directory')
        parser.add_argument('--app_name', type=str, default='users',
                            help='Name of the auth app (e.g. users, accounts)')
        parser.add_argument('--view_type', type=str, default='Class Based',
                            help='View style: "Class Based" or "Function Based"')
        return parser


# Module-level shim for existing callers
def generate_django_custom_auth_apis_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoCustomAuthApisExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoCustomAuthApisExecutor.build_arg_parser().parse_args()
    DjangoCustomAuthApisExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
        view_type=args.view_type,
    )
