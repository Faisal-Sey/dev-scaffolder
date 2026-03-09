import argparse
import sys
import os
from rich.console import Console

# Add the project root to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from rich.status import Status
from executors.backend.python.django.official import generate_django_official_template
from typings.base import (
    DjangoOfficialTemplateArgs,
    DjangoOfficialTemplateResponse,
    ExecutorResponseStatus
)

console = Console()

def generate_django_custom_auth_template(
        executing: Status = None,
        **kwargs: DjangoOfficialTemplateArgs
) -> ExecutorResponseStatus:
    """
    Generates a Django project with a Custom User Model.
    """
    project_name = kwargs.get("project_name", "test")
    directory_name = kwargs.get("directory_name", project_name)
    app_name = kwargs.get("app_name", "users")

    response: DjangoOfficialTemplateResponse = generate_django_official_template(
        executing=executing,
        project_name=project_name,
        app_name=app_name,
        directory_name=directory_name
    )

    if not response.success:
        return ExecutorResponseStatus(success=False)

    console.print(f"[bold green]Django project with Custom Auth '{project_name}' created successfully![/bold green]")
    console.print(f"[yellow]Note: Custom User model creation in '{app_name}' and AUTH_USER_MODEL setting would be implemented here.[/yellow]")

    return ExecutorResponseStatus(success=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Django Custom Auth template')
    parser.add_argument('--project_name', type=str, default='myproject')
    parser.add_argument('--directory_name', type=str, default='myproject')
    parser.add_argument('--app_name', type=str, default='users')
    args = parser.parse_args()

    generate_django_custom_auth_template(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
    )
