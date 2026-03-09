import argparse
from rich.console import Console

console = Console()

def generate_spring_boot_template(**kwargs):
    project_name = kwargs.get("project_name", "demo")
    group_id = kwargs.get("group_id", "com.example")
    use_maven = kwargs.get("use_maven", True)
    
    console.print(f"[bold green]Generating Spring Boot project: {project_name}[/bold green]")
    console.print(f"Group ID: {group_id}")
    console.print(f"Build Tool: {'Maven' if use_maven else 'Gradle'}")
    # Implementation placeholder
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Spring Boot template')
    parser.add_argument('--project_name', type=str, default='demo')
    parser.add_argument('--group_id', type=str, default='com.example')
    parser.add_argument('--use_maven', type=bool, default=True)
    args = parser.parse_args()

    generate_spring_boot_template(
        project_name=args.project_name,
        group_id=args.group_id,
        use_maven=args.use_maven
    )
