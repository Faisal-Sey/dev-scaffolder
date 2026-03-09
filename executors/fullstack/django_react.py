import argparse

def generate_fullstack_django_react(project_name="my_django_react_project", use_docker=False):
    print(f"Generating Django + React fullstack project: {project_name}")
    print(f"Use Docker: {use_docker}")
    # Placeholder for actual generation logic

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Django + React fullstack project')
    parser.add_argument('--project_name', type=str, default='my_django_react_project')
    parser.add_argument('--use_docker', type=bool, default=False)
    args = parser.parse_args()
    generate_fullstack_django_react(project_name=args.project_name, use_docker=args.use_docker)
