import argparse
import sys
import os
from rich.console import Console

# Add the project root to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from rich.status import Status
from typings.base import ExecutorResponseStatus

console = Console()

def generate_nest_template(
        executing: Status = None,
        **kwargs
) -> ExecutorResponseStatus:
    """
    Generates a NestJS project.
    """
    project_name = kwargs.get("project_name", "my-nest-app")

    console.print(f"[bold green]NestJS project '{project_name}' created successfully![/bold green]")
    console.print("[yellow]Note: NestJS CLI integration would be implemented here.[/yellow]")

    return ExecutorResponseStatus(success=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate NestJS template')
    parser.add_argument('--project_name', type=str, default='my-nest-app')
    args = parser.parse_args()

    generate_nest_template(
        project_name=args.project_name
    )
