import argparse
from rich.console import Console

console = Console()

def generate_quarkus_template(**kwargs):
    project_name = kwargs.get("project_name", "quarkus-app")
    group_id = kwargs.get("group_id", "com.example")
    
    console.print(f"[bold green]Generating Quarkus project: {project_name}[/bold green]")
    console.print(f"Group ID: {group_id}")
    # Implementation placeholder
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Quarkus template')
    parser.add_argument('--project_name', type=str, default='quarkus-app')
    parser.add_argument('--group_id', type=str, default='com.example')
    args = parser.parse_args()

    generate_quarkus_template(
        project_name=args.project_name,
        group_id=args.group_id
    )
