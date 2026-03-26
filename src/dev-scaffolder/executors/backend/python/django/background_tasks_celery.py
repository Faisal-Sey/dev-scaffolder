import argparse

def generate_template(**kwargs):
    print(f"Generating template with args: {kwargs}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_name", type=str, default="my-django-project")
    parser.add_argument("--redis_url", type=str, default="redis://localhost:6379/0")
    args = parser.parse_args()
    generate_template(project_name=args.project_name, redis_url=args.redis_url)
