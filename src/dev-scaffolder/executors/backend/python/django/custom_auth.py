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
)
from utils.base import get_venv_python_executor


class DjangoCustomAuthExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django project with a custom User model.

    Builds on DjangoOfficialExecutor by:
      - Adding the auth app to INSTALLED_APPS
      - Setting AUTH_USER_MODEL to point at the custom User model
      - Writing a custom User model (extends AbstractUser)
      - Registering the model in admin with CustomUserAdmin
      - Creating UserCreationForm / UserChangeForm subclasses in forms.py

    No extra packages are required — all functionality comes from Django itself.
    """

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        # Custom auth uses only Django built-ins — no extra packages needed.
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    def _insert_app_re(self, content: str, new_app: str) -> str:
        """Append a new app entry at the end of the INSTALLED_APPS list."""
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'

        def insert_app(match):
            prefix = match.group(1)
            apps_content = match.group(2).rstrip()
            suffix = match.group(3)
            if apps_content.strip() and not apps_content.strip().endswith(','):
                apps_content += ','
            return f"{prefix}{apps_content}\n    '{new_app}',\n{suffix}"

        return re.sub(pattern, insert_app, content, flags=re.DOTALL)

    def _set_auth_user_model(self, settings_path: str, app_name: str) -> None:
        """Append AUTH_USER_MODEL after the INSTALLED_APPS block."""
        try:
            with open(settings_path, 'a') as f:
                f.write(f"\n\nAUTH_USER_MODEL = '{app_name}.User'\n")
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

    def _add_to_installed_apps(self, settings_path: str, app_name: str) -> None:
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            content = self._insert_app_re(content, app_name)
            with open(settings_path, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f"[bold red]File not found: {settings_path}[/bold red]")

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

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django project and configures a custom User model.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the auth app (e.g. 'users', 'accounts').
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

        if response.message == "APP_CREATION_FAILED":
            self.console.print("[bold red]App creation failed — cannot configure custom auth[/bold red]")
            return ExecutorResponseStatus(success=False)

        project_path = response.path
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        app_path = os.path.join(project_path, app_name)

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

        self._update_status("[bold blue]Updating requirements.txt...[/bold blue]")
        venv_python_executor = get_venv_python_executor()
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self._update_status("[bold blue]Writing README.md...[/bold blue]")
        self._write_readme(project_path, project_name=project_name, app_name=app_name)

        self.console.print(
            f"[bold green]Django custom auth project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        """
        Internal implementation for generating the Django custom auth template.

        Resolves arguments and delegates to execute_creation_commands.
        Called by run(); do not call directly.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the auth app.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs.get("project_name", "test") or "test"
        directory_name = kwargs.get("directory_name", "") or project_name
        app_name = kwargs.get("app_name", "users") or "users"

        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
        )

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get("project_name", "project")
        app_name = kwargs.get("app_name", "users")
        return (
            f"# {project_name}\n\n"
            "A Django project with a custom User model, scaffolded with dev-scaffolder.\n\n"
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
            "Apply migrations for the custom `User` model before running:\n\n"
            "```bash\n"
            "python manage.py makemigrations\n"
            "python manage.py migrate\n"
            "```\n\n"
            "## Create a superuser\n\n"
            "```bash\n"
            "python manage.py createsuperuser\n"
            "```\n\n"
            "## Run\n\n"
            "```bash\n"
            "python manage.py runserver\n"
            "```\n\n"
            "Open http://localhost:8000 in your browser.\n\n"
            "## Admin\n\n"
            f"Visit http://localhost:8000/admin/ to manage users via the `{app_name}` app.\n"
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
        return parser


# Module-level shim so existing callers using generate_django_custom_auth_template() still work
def generate_django_custom_auth_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoCustomAuthExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoCustomAuthExecutor.build_arg_parser().parse_args()
    DjangoCustomAuthExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
    )
