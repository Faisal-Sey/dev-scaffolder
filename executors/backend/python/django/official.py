import os.path
import shutil
import subprocess
import sys
import argparse
from pathlib import Path
from typing import TypedDict

import inquirer

# Add the project root to sys.path
# Fix - ModuleNotFoundError: No module named 'processor'
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from utils.base import check_or_create_venv, get_venv_python_executor, activate_venv, run_subprocess_command
from typings.base import DjangoOfficialTemplateArgs, DjangoOfficialTemplateResponse, ExecutorResponseStatus

current_folder = os.getcwd()


def get_venv_environment() -> str:
    """
    Retrieves the Python executable path for the current virtual environment. This method ensures that
    a virtual environment exists, activates it, and determines the Python interpreter associated with it.

    :return: The path to the Python executable for the active virtual environment.
    :rtype: str
    """

    # check virtual environment
    check_or_create_venv()

    # activate venv
    activate_venv()

    # get python executor to install packages in the current venv
    venv_python_executor = get_venv_python_executor()

    return venv_python_executor


def install_dependencies(
        venv_python_executor: str,
) -> ExecutorResponseStatus:
    """
    Installs the Django dependencies using the provided Python virtual environment executor.

    This function attempts to install Django by invoking the appropriate command
    via the provided Python executor for a virtual environment. If the installation
    fails, the function outputs an error message and stops further execution.
    Otherwise, it confirms the successful installation.

    :param venv_python_executor: Path to the Python executor within a virtual
        environment to be used for installing packages.
    :type venv_python_executor: str
    :return: ExecutorResponseStatus
    :rtype: ExecutorResponseStatus
    """

    # django packages commands
    project_command = [venv_python_executor, '-m', 'pip', 'install', 'django']

    install_django = run_subprocess_command(project_command)
    if not install_django:
        print("Failed to install django")
        return ExecutorResponseStatus(success=False)

    print("Django installed successfully")
    return ExecutorResponseStatus(success=True)


def add_packages_to_requirements_txt(venv_python_executor: str, project_name: str) -> None:
    print(os.getcwd())
    os.chdir(os.path.join(current_folder, project_name))
    result = subprocess.run(
        [venv_python_executor, '-m', 'pip', 'freeze'],
        capture_output=True,
        text=True,
        check=True
    )

    # Write output to requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write(result.stdout)

    os.chdir(os.path.join(current_folder))


def create_django_project(
        project_name: str,
        directory_name: str,
) -> ExecutorResponseStatus:
    """
    Creates a new Django project in the specified directory.

    This function initializes a Django project using the ``django-admin`` command. It
    requires Django to be installed and correctly configured in the environment where
    the function is executed. If the project creation fails, an error message is printed,
    and no further action is taken.

    :param project_name: Name of the Django project to be created.
    :param directory_name: Path of the directory where the Django project will be
        created.
    :return: ExecutorResponseStatus
    """

    # create a project on successful django installation
    # django packages commands
    create_project_command = [
        'django-admin',
        'startproject',
        project_name,
        directory_name
    ]

    create_project = run_subprocess_command(create_project_command)
    if not create_project:
        print("Failed to create django project")
        return ExecutorResponseStatus(success=False)

    print(f"Django project {project_name} created successfully.")
    return ExecutorResponseStatus(success=True)


def create_django_app(app_name: str, project_name: str) -> ExecutorResponseStatus:
    """
    Create a new Django application using the specified application name.

    This function executes the Django command-line utility to generate a new app,
    and it validates whether the app creation process succeeds or not. If the app
    name is not provided, the function skips the app creation process.

    :param app_name: The name of the Django application to create.
    :type app_name: str
    :param project_name: The name of the Django project.
    :type project_name: str
    :return: ExecutorResponseStatus
    """

    # change directory to the project directory
    os.chdir(project_name)

    create_app_command = [
        'django-admin',
        'startapp',
        app_name,
    ]

    if app_name:
        create_app = run_subprocess_command(create_app_command)

        if not create_app:
            print("Failed to create django app")
            return ExecutorResponseStatus(success=False)
        else:
            print(f"Django app {app_name} created successfully.")
    else:
        print("Skip django app creation")

    return ExecutorResponseStatus(success=True)


def execute_creation_commands(
        project_name: str,
        directory_name: str,
        app_name: str
) -> ExecutorResponseStatus:
    """
    Executes a sequence of commands to set up a Django project and application.

    This function automates the creation of a Django project and application by performing
    a series of steps, including creating a virtual environment, installing dependencies,
    and initializing the Django project and app.

    :param project_name: Name of the Django project to be created.
    :type project_name: str
    :param directory_name: Name of the directory where the Django project will be created.
    :type directory_name: str
    :param app_name: Name of the Django application to be initialized within the project.
    :type app_name: str
    :return: ExecutorResponseStatus
    :rtype: ExecutorResponseStatus
    """

    venv_python_executor = get_venv_python_executor()
    installation_response = install_dependencies(venv_python_executor)
    if not installation_response.success:
        print("Failed to install django")
        return ExecutorResponseStatus(success=False)

    project_creation_response = create_django_project(
        project_name,
        directory_name,
    )
    if not project_creation_response.success:
        print("Failed to create django project")
        return ExecutorResponseStatus(success=False)

    add_packages_to_requirements_txt(venv_python_executor, project_name)

    project_directory = os.path.join(current_folder, directory_name)
    app_creation_response = create_django_app(app_name, project_directory)
    if not app_creation_response.success:
        print("Project created successfully. Failed at app creation")
        return ExecutorResponseStatus(success=True, message="APP_CREATION_FAILED")

    return ExecutorResponseStatus(success=True)


def prepare_directory(directory_full_path: str) -> ExecutorResponseStatus:
    """
    Ensures the specified directory is prepared for use by either creating it or replacing
    its content if it already exists. If the directory matches the current folder, the function
    warns the user and exits to prevent accidental deletion of critical data. It presents
    a confirmation prompt to the user before replacing an existing directory. If the user denies
    replacement, no changes are made.

    :param directory_full_path: The absolute or relative path to the target directory.
    :type directory_full_path: str
    :return: ExecutorResponseStatus if the operation is aborted or completed successfully.
    :rtype: ExecutorResponseStatus
    """

    # Ensure directory_full_path is not equal to the current folder to avoid accidental deletion
    if os.path.abspath(directory_full_path) == os.path.abspath(current_folder):
        print("Cannot delete the root directory")
        return ExecutorResponseStatus(success=False)

    is_directory_exist = os.path.exists(directory_full_path)
    if is_directory_exist:
        # ask for user consent
        prompt = [
            inquirer.Confirm(
                "replace_directory",
                message="Directory exists, do you want to replace the content",
                default=True
            )
        ]
        replace_directory_answers = inquirer.prompt(prompt)
        if replace_directory_answers is None:
            print("You selected a wrong option")
            return ExecutorResponseStatus(success=False)

        replace_directory = replace_directory_answers.get("replace_directory")
        if replace_directory:
            # delete directory and recreate
            shutil.rmtree(directory_full_path)
            os.makedirs(directory_full_path)
        else:
            return ExecutorResponseStatus(success=False)
    else:
        # create a directory if it does not exist
        os.makedirs(directory_full_path)

    return ExecutorResponseStatus(success=True)


def generate_django_official_template(**kwargs: DjangoOfficialTemplateArgs) -> DjangoOfficialTemplateResponse:
    """
    Generates the official Django project template by setting up all necessary folders
    and executing creation commands. The process ensures the directory is properly
    prepared and named before the project and application are initialized with
    minimal customization options.

    :param kwargs: Arbitrary keyword arguments containing optional custom inputs
        for the project and app creation process.
        - project_name (str): The name of the Django project.
        - directory_name (str): The name of the directory to create or clean.
        - app_name (str): The name of the application to initialize within the
          project directory.

    :return: DjangoOfficialTemplateResponse
    """

    # default project_name to test
    project_name = kwargs.get("project_name", "test")
    if not project_name:
        project_name = "test"

    directory_name = kwargs.get("directory_name", "")
    app_name = kwargs.get("app_name", "")

    if (directory_name is None) or (not directory_name):
        directory_name = project_name

    directory_full_path = os.path.join(current_folder, directory_name)

    # create or clean a directory
    preparation_response = prepare_directory(directory_full_path)
    if not preparation_response.success:
        return DjangoOfficialTemplateResponse(success=False)

    success = preparation_response.success

    if success:
        creation_response: ExecutorResponseStatus = execute_creation_commands(
            project_name,
            directory_name,
            app_name
        )

        return DjangoOfficialTemplateResponse(
            success=creation_response.success,
            message=creation_response.message,
            path=directory_full_path
        )

    return DjangoOfficialTemplateResponse(
        success=success,
        path=directory_full_path
    )


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

    generate_django_official_template(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name
    )