import argparse

def generate_aspnet_core(project_name="MyProject", template="webapi", use_docker=False):
    print(f"Generating ASP.NET Core project: {project_name}")
    print(f"Template: {template}")
    print(f"Docker Support: {use_docker}")
    # Placeholder for actual generation logic

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASP.NET Core Project Generator")
    parser.add_argument("--project_name", type=str, default="MyProject")
    parser.add_argument("--template", type=str, default="webapi")
    parser.add_argument("--use_docker", type=bool, default=False)
    args = parser.parse_args()
    
    generate_aspnet_core(args.project_name, args.template, args.use_docker)
