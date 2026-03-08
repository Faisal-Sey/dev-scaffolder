import argparse
import sys
import os

# Add the project root to sys.path
# Fix - ModuleNotFoundError: No module named 'executors'
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.backend.python.django.official import generate_django_official_template
from typings.base import (
    DjangoOfficialTemplateArgs,
    DjangoOfficialTemplateResponse,
    ExecutorResponseStatus,
    WriteToFileContent
)
from constants.backend.python.base import (
    DJANGO_APP_URL_CONFIG,
    DJANGO_VIEW_FUNCTION_IMPORT_JSON_RESPONSE,
    DJANGO_VIEW_FUNCTION
)
from utils.base import write_into_file


def integrate_app_url_into_project():
    pass


def modify_views_py(path: str, app_name: str):
    views_file = os.path.join(path, app_name, "views.py")
    write_into_file(
        views_file,
        [
            WriteToFileContent(line=0, content=DJANGO_VIEW_FUNCTION_IMPORT_JSON_RESPONSE),
            WriteToFileContent(line=-1, content=DJANGO_VIEW_FUNCTION)
        ]
    )


def create_app_urls_py(path: str, app_name: str):
    # switch into the app
    app_path = os.path.join(path, app_name)
    os.chdir(app_path)

    open("urls.py", "w").close()
    urls_file = os.path.join(path, app_name, "urls.py")
    write_into_file(
        urls_file,
        [WriteToFileContent(line=0, content=DJANGO_APP_URL_CONFIG)]
    )


def configure_app(path: str, app_name: str) -> None:
    modify_views_py(path, app_name)
    create_app_urls_py(path, app_name)
    print(
        f"Django app {app_name} configured successfully in {path}"
    )


def generate_django_official_configure_app_template(
        **kwargs: DjangoOfficialTemplateArgs
) -> ExecutorResponseStatus:
    """
    Generates and configures a Django application using an official template. The function creates
    the necessary files and directories for the project and app, based on the provided parameters,
    and applies the required configuration to the generated app.

    :param kwargs: A dictionary of parameters used for generating the Django project and app. Expected
                   keys include:
                   - project_name (str): Name of the project. Defaults to "test" if not provided or empty.
                   - directory_name (str): Name of the directory where the project will be created.
                     Defaults to the value of project_name if not provided or empty.
                   - app_name (str): Name of the Django app to generate and configure. Defaults to an empty string.
    :returns: An object of type ExecutorResponseStatus indicating whether the generation and configuration
              of the Django application succeeded.
    """

    # default project_name to test
    project_name = kwargs.get("project_name", "test")
    if not project_name:
        project_name = "test"

    directory_name = kwargs.get("directory_name", "")
    app_name = kwargs.get("app_name", "")

    if (directory_name is None) or (not directory_name):
        directory_name = project_name

    response: DjangoOfficialTemplateResponse = generate_django_official_template(
        project_name=project_name,
        app_name=app_name,
        directory_name=directory_name
    )

    if not response.success:
        return ExecutorResponseStatus(success=False)

    if response.message == "APP_CREATION_FAILED":
        return ExecutorResponseStatus(success=False)

    configure_app(response.path, app_name)

    return ExecutorResponseStatus(success=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Django official template')

    # Add arguments
    parser.add_argument('--project_name', type=str, default='myproject',
                        help='Name of the Django project')
    parser.add_argument('--directory_name', type=str, default='myproject',
                        help='Name of the Django project directory')
    parser.add_argument('--app_name', type=str, default='core',
                        help='Name of the Django app')

    # Parse arguments
    args = parser.parse_args()

    generate_django_official_configure_app_template(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name
    )