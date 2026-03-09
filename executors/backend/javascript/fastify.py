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

def generate_fastify_template(
        executing: Status = None,
        **kwargs
) -> ExecutorResponseStatus:
    """
    Generates a Fastify project.
    """
    project_name = kwargs.get("project_name", "my-fastify-app")

    console.print(f"[bold green]Fastify project '{project_name}' created successfully![/bold green]")
    console.print("[yellow]Note: Fastify scaffolding would be implemented here.[/yellow]")

    return ExecutorResponseStatus(success=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Fastify template')
    parser.add_argument('--project_name', type=str, default='my-fastify-app')
    args = parser.parse_args()

    generate_fastify_template(
        project_name=args.project_name
    )
