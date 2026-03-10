import os
import subprocess
import sys
import argparse
from typing import cast

# Add the project root to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from utils.base import check_or_create_venv, get_venv_python_executor, activate_venv, run_subprocess_command
from typings.base import DjangoOfficialTemplateArgs, DjangoOfficialTemplateResponse, ExecutorResponseStatus


class DjangoOfficialExecutor(BaseExecutor):
    """
    Executor for scaffolding an official Django project.

    Handles virtual environment setup, Django installation, project and app
    creation, and requirements generation.
    """

    def get_venv_environment(self) -> str:
        """
        Retrieves the Python executable path for the current virtual environment.

        Ensures a virtual environment exists, activates it, and returns the path
        to the Python interpreter inside it.

        :return: Path to the venv Python executable.
        :rtype: str
        """
        check_or_create_venv()
        activate_venv()
        return get_venv_python_executor()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        """
        Installs Django using the provided virtual environment Python executable.

        :param venv_python_executor: Path to the venv Python executable.
        :type venv_python_executor: str
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_command = [venv_python_executor, '-m', 'pip', 'install', 'django']
        if not run_subprocess_command(project_command):
            self.console.print("[bold red]Failed to install django[/bold red]")
            return ExecutorResponseStatus(success=False)

        self.console.print("[bold green]Django installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def _add_packages_to_requirements_txt(self, venv_python_executor: str, project_name: str) -> None:
        os.chdir(os.path.join(self.current_folder, project_name))
        result = subprocess.run(
            [venv_python_executor, '-m', 'pip', 'freeze'],
            capture_output=True,
            text=True,
            check=True
        )
        with open('requirements.txt', 'w') as f:
            f.write(result.stdout)
        os.chdir(self.current_folder)

    def _create_django_project(self, project_name: str, directory_name: str) -> ExecutorResponseStatus:
        create_project_command = ['django-admin', 'startproject', project_name, directory_name]
        if not run_subprocess_command(create_project_command):
            self.console.print("[bold red]Failed to create django project[/bold red]")
            return ExecutorResponseStatus(success=False)

        self.console.print(f"[bold green]Django project {project_name} created successfully.[/bold green]")
        return ExecutorResponseStatus(success=True)

    def _create_django_app(self, app_name: str, project_directory: str) -> ExecutorResponseStatus:
        os.chdir(project_directory)
        create_app_command = ['django-admin', 'startapp', app_name]

        if app_name:
            if not run_subprocess_command(create_app_command):
                self.console.print("[bold red]Failed to create django app[/bold red]")
                return ExecutorResponseStatus(success=False)
            self.console.print(f"[bold green]Django app {app_name} created successfully.[/bold green]")
        else:
            self.console.print("[yellow]Skip django app creation[/yellow]")

        return ExecutorResponseStatus(success=True)

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Orchestrates venv setup, dependency installation, project and app creation.

        Updates the spinner message for each step instead of creating nested
        console.status() contexts.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app to create inside the project.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs["project_name"]
        directory_name = kwargs["directory_name"]
        app_name = kwargs["app_name"]

        venv_python_executor = get_venv_python_executor()

        self._update_status("[bold blue]Installing dependencies...[/bold blue]")
        installation_response = self.install_dependencies(venv_python_executor)
        if not installation_response.success:
            self.console.print("[bold red]Failed to install django[/bold red]")
            return ExecutorResponseStatus(success=False)

        self._update_status(f"[bold blue]Creating Django project '{project_name}'...[/bold blue]")
        project_creation_response = self._create_django_project(project_name, directory_name)
        if not project_creation_response.success:
            self.console.print("[bold red]Failed to create django project[/bold red]")
            return ExecutorResponseStatus(success=False)

        self._update_status("[bold blue]Generating requirements.txt...[/bold blue]")
        self._add_packages_to_requirements_txt(venv_python_executor, project_name)

        project_directory = cast(str, os.path.join(self.current_folder, directory_name))
        self._update_status(f"[bold blue]Creating Django app '{app_name}'...[/bold blue]")
        app_creation_response = self._create_django_app(app_name, project_directory)
        if not app_creation_response.success:
            self.console.print("[bold yellow]Project created successfully. Failed at app creation[/bold yellow]")
            return ExecutorResponseStatus(success=True, message="APP_CREATION_FAILED")

        return ExecutorResponseStatus(success=True)

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> DjangoOfficialTemplateResponse:
        """
        Internal implementation for generating the official Django project template.

        Resolves arguments, prepares the directory, and invokes execute_creation_commands.
        Called by run(); do not call directly.

        :param kwargs: Keyword arguments for project configuration.
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app.
        :return: DjangoOfficialTemplateResponse with success status and output path.
        :rtype: DjangoOfficialTemplateResponse
        """
        project_name = kwargs.get("project_name", "test") or "test"
        directory_name = kwargs.get("directory_name", "") or project_name
        app_name = kwargs.get("app_name", "")

        directory_full_path = cast(str, os.path.join(self.current_folder, directory_name))

        preparation_response = self.prepare_directory(directory_full_path)
        if not preparation_response.success:
            return DjangoOfficialTemplateResponse(success=False)

        creation_response = self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
        )

        return DjangoOfficialTemplateResponse(
            success=creation_response.success,
            message=creation_response.message,
            path=directory_full_path
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject',
                            help='Name of the Django project')
        parser.add_argument('--directory_name', type=str, default='myproject',
                            help='Name of the Django project directory')
        parser.add_argument('--app_name', type=str, default='',
                            help='Name of the Django app')
        return parser


# Module-level shim so existing callers using generate_django_official_template() still work
def generate_django_official_template(**kwargs) -> DjangoOfficialTemplateResponse:
    return DjangoOfficialExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoOfficialExecutor.build_arg_parser().parse_args()
    DjangoOfficialExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
    )