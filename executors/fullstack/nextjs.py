import argparse

def generate_fullstack_nextjs(project_name="my_nextjs_project", use_typescript=True, use_tailwind=True, use_app_router=True):
    print(f"Generating Next.js fullstack project: {project_name}")
    print(f"Use TypeScript: {use_typescript}")
    print(f"Use Tailwind CSS: {use_tailwind}")
    print(f"Use App Router: {use_app_router}")
    # Placeholder for actual generation logic

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Next.js fullstack project')
    parser.add_argument('--project_name', type=str, default='my_nextjs_project')
    parser.add_argument('--use_typescript', type=bool, default=True)
    parser.add_argument('--use_tailwind', type=bool, default=True)
    parser.add_argument('--use_app_router', type=bool, default=True)
    args = parser.parse_args()
    generate_fullstack_nextjs(
        project_name=args.project_name, 
        use_typescript=args.use_typescript,
        use_tailwind=args.use_tailwind,
        use_app_router=args.use_app_router
    )
