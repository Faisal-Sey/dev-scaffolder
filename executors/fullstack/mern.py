import argparse

def generate_fullstack_mern(project_name="my_mern_project", use_typescript=False):
    print(f"Generating MERN fullstack project: {project_name}")
    print(f"Use TypeScript: {use_typescript}")
    # Placeholder for actual generation logic

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate MERN fullstack project')
    parser.add_argument('--project_name', type=str, default='my_mern_project')
    parser.add_argument('--use_typescript', type=bool, default=False)
    args = parser.parse_args()
    generate_fullstack_mern(project_name=args.project_name, use_typescript=args.use_typescript)
