import argparse
from rich.console import Console

console = Console()

def generate_micronaut_template(**kwargs):
    project_name = kwargs.get("project_name", "micronaut-app")
    base_package = kwargs.get("base_package", "com.example")
    
    console.print(f"[bold green]Generating Micronaut project: {project_name}[/bold green]")
    console.print(f"Base Package: {base_package}")
    # Implementation placeholder
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Micronaut template')
    parser.add_argument('--project_name', type=str, default='micronaut-app')
    parser.add_argument('--base_package', type=str, default='com.example')
    args = parser.parse_args()

    generate_micronaut_template(
        project_name=args.project_name,
        base_package=args.base_package
    )
