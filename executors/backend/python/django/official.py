import os.path
import shutil
import subprocess
import sys
import argparse
from pathlib import Path
from typing import TypedDict

import inquirer

# Add project root to sys.path
# Fix - ModuleNotFoundError: No module named 'processor'
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from typings.base import SubProcessReturnCodeEnum
from utils.base import check_or_create_venv, get_venv_python_executor, activate_venv

root_folder = Path(__file__).parent.parent.parent.parent.parent


class DjangoOfficialTemplateArgs(TypedDict):
    """
    Represents a typed dictionary for Django official template arguments.

    This class is used to define a structure for the arguments required to set up
    a Django project using the official template. It ensures that the provided
    data adheres to the specified keys and value types, which are typically used to
    initialize a Django project directory and structure.

    :ivar project_name: The name of the Django project.
    :type project_name: str
    :ivar directory_name: The name of the directory where the project will be created.
    :type directory_name: str
    """
    project_name: str
    directory_name: str


def execute_creation_commands(
        project_name: str,
        directory_name: str,
        app_name: str
):
    # check virtual environment
    check_or_create_venv()

    # get python executor to install packages in the current venv
    venv_python_executor = get_venv_python_executor()

    activate_venv()

    # django packages commands
    project_command = [venv_python_executor, '-m', 'pip', 'install', 'django']

    install_django = subprocess.run(project_command, capture_output=True, text=True)
    if install_django.returncode != SubProcessReturnCodeEnum.SUCCESS.value:
        print("Failed to install django")
        # TODO: to be improved
        return None

    # create a project on successful django installation
    # django packages commands
    create_project_command = [
        'django-admin',
        'startproject',
        project_name,
        directory_name
    ]
    create_app_command = [
        'django-admin',
        'startapp',
        app_name,
    ]

    create_project = subprocess.run(create_project_command)
    if create_project.returncode != SubProcessReturnCodeEnum.SUCCESS.value:
        print("Failed to create django project")
        # TODO: to be improved
        return None
    else:
        print(f"Django project {project_name} created successfully.")

    if app_name:
        create_app = subprocess.run(create_app_command, capture_output=True, text=True)
        if create_app.returncode != SubProcessReturnCodeEnum.SUCCESS.value:
            print("Failed to create django app")
        else:
            print(f"Django app {app_name} created successfully.")

    return None


def generate_django_official_template(**kwargs: DjangoOfficialTemplateArgs):
    # default project_name to test
    project_name = kwargs.get("project_name", "test")
    if not project_name:
        project_name = "test"

    directory_name = kwargs.get("directory_name", "")
    app_name = kwargs.get("app_name", "")

    if (directory_name is None) or (not directory_name):
        directory_name = project_name

    directory_full_path = os.path.join(root_folder, directory_name)

    # Ensure directory_full_path is not equal to root_folder to avoid accidental deletion
    if os.path.abspath(directory_full_path) == os.path.abspath(root_folder):
        print("Cannot delete the root directory")
        return None

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
            return None

        replace_directory = replace_directory_answers.get("replace_directory")
        if replace_directory:
            # delete directory and recreate
            shutil.rmtree(directory_full_path)
            os.makedirs(directory_full_path)
        else:
            return None
    else:
        # create a directory if it does not exist
        os.makedirs(directory_full_path)

    execute_creation_commands(
        project_name,
        directory_name,
        app_name
    )

    return None

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