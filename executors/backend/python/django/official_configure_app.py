import argparse
import sys
import os

# Add the project root to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
    WriteToFileContent
)
from constants.backend.python.base import (
    DJANGO_APP_URL_CONFIG,
    DJANGO_VIEW_FUNCTION_IMPORT_JSON_RESPONSE,
    DJANGO_VIEW_FUNCTION,
)
from utils.base import write_into_file, get_venv_python_executor


class DjangoOfficialConfigureAppExecutor(BaseExecutor):
    """
    Executor that scaffolds an official Django project and then configures
    the generated app with a starter views.py, urls.py, and project URL wiring.

    Delegates project/app creation to DjangoOfficialExecutor and shares the
    active spinner with it so interactive prompts (e.g. directory replacement)
    are handled correctly.
    """

    def get_venv_environment(self) -> str:
        """
        Delegates venv setup to DjangoOfficialExecutor.

        :return: Path to the venv Python executable.
        :rtype: str
        """
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        """
        Dependencies are installed by DjangoOfficialExecutor during project
        scaffolding, so no additional installation is required here.

        :param venv_python_executor: Path to the venv Python executable.
        :type venv_python_executor: str
        :return: ExecutorResponseStatus indicating success.
        :rtype: ExecutorResponseStatus
        """
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # App configuration helpers
    # ------------------------------------------------------------------

    def _integrate_app_url_into_project(self, path: str, directory_name: str, app_name: str) -> None:
        """
        Integrate the app urls.py in the project urls

        :param path: The current folder the project folder is in
        :type path: str
        :param directory_name: The project folder name
        :type directory_name: str
        :param app_name: The app name
        :type app_name: str
        :return: None
        :rtype: None
        """
        project_urls_path = os.path.join(path, directory_name, "urls.py")
        try:
            with open(project_urls_path, 'r') as f:
                content = f.read()

            modified_content = content.replace(
                'urlpatterns = [\n',
                (
                    "urlpatterns = [\n"
                    f"  path('{app_name}/', include('{app_name}.urls')),\n"
                )
            )
            modified_content = modified_content.replace(
                "from django.urls import path",
                "from django.urls import path, include"
            )

            with open(project_urls_path, "w") as f:
                f.write(modified_content)

        except FileNotFoundError:
            self.console.print(
                f"[bold red]File was not found at {project_urls_path}[/bold red]"
            )

    def _modify_views_py(self, path: str, app_name: str) -> None:
        views_file = os.path.join(path, app_name, "views.py")
        write_into_file(
            views_file,
            [
                WriteToFileContent(line=0, content=DJANGO_VIEW_FUNCTION_IMPORT_JSON_RESPONSE),
                WriteToFileContent(line=-1, content=DJANGO_VIEW_FUNCTION)
            ]
        )

    def _create_app_urls_py(self, path: str, app_name: str) -> None:
        app_path = os.path.join(path, app_name)
        os.chdir(app_path)
        open("urls.py", "w").close()
        urls_file = os.path.join(path, app_name, "urls.py")
        write_into_file(
            urls_file,
            [WriteToFileContent(line=0, content=DJANGO_APP_URL_CONFIG)]
        )

    def _configure_app(self, path: str, app_name: str, directory_name: str) -> None:
        self._modify_views_py(path, app_name)
        self._create_app_urls_py(path, app_name)
        self._integrate_app_url_into_project(path, directory_name, app_name)

        venv_python_executor = get_venv_python_executor()

        # Re-freeze requirements after app configuration
        django_executor = DjangoOfficialExecutor()
        django_executor.add_packages_to_requirements_txt(venv_python_executor, path)

        self.console.print(
            f"[bold green]Django app {app_name} configured successfully in {path}[/bold green]"
        )

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds the Django project/app via DjangoOfficialExecutor, then
        configures the app with starter views, urls, and project URL wiring.

        Shares the active spinner with the inner executor so the directory
        replacement prompt is handled correctly without spinner conflicts.

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

        # Share the active spinner so prepare_directory can pause/resume it
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
            self.console.print("[bold red]App creation failed — cannot configure app[/bold red]")
            return ExecutorResponseStatus(success=False)

        self._update_status(f"[bold blue]Configuring Django app '{app_name}'...[/bold blue]")
        self._configure_app(response.path, app_name, directory_name)

        return ExecutorResponseStatus(success=True)

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        """
        Internal implementation for generating and configuring the Django app template.

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
        app_name = kwargs.get("app_name", "")

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
        parser.add_argument('--app_name', type=str, default='core',
                            help='Name of the Django app')
        return parser


# Module-level shim so existing callers using generate_django_official_configure_app_template() still work
def generate_django_official_configure_app_template(**kwargs) -> ExecutorResponseStatus:
    return DjangoOfficialConfigureAppExecutor().run(**kwargs)


if __name__ == '__main__':
    args = DjangoOfficialConfigureAppExecutor.build_arg_parser().parse_args()
    DjangoOfficialConfigureAppExecutor().run(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
    )