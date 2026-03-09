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

def generate_django_rest_framework_template(
        executing: Status = None,
        **kwargs: DjangoOfficialTemplateArgs
) -> ExecutorResponseStatus:
    """
    Generates a Django project with REST Framework.
    """
    project_name = kwargs.get("project_name", "test")
    directory_name = kwargs.get("directory_name", project_name)
    app_name = kwargs.get("app_name", "")

    response: DjangoOfficialTemplateResponse = generate_django_official_template(
        executing=executing,
        project_name=project_name,
        app_name=app_name,
        directory_name=directory_name
    )

    if not response.success:
        return ExecutorResponseStatus(success=False)

    console.print(f"[bold green]Django project with REST Framework '{project_name}' created successfully![/bold green]")
    console.print("[yellow]Note: DRF installation and settings configuration would be implemented here.[/yellow]")

    return ExecutorResponseStatus(success=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Django REST Framework template')
    parser.add_argument('--project_name', type=str, default='myproject')
    parser.add_argument('--directory_name', type=str, default='myproject')
    parser.add_argument('--app_name', type=str, default='')
    args = parser.parse_args()

    generate_django_rest_framework_template(
        project_name=args.project_name,
        app_name=args.app_name,
        directory_name=args.directory_name,
    )
