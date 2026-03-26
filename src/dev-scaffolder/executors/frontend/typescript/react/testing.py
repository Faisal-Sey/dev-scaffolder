import argparse

def generate_template(**kwargs):
    print(f"Generating template with args: {kwargs}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_name", type=str, default="my-project")
    args = parser.parse_args()
    generate_template(project_name=args.project_name)
