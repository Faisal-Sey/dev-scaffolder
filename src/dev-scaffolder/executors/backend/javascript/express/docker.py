import argparse
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from batteries.registry import parse_express_batteries
from typings.base import ExecutorResponseStatus
from constants.backend.javascript.express.base import (
    EXPRESS_DOCKERFILE,
    EXPRESS_DOCKER_COMPOSE,
    EXPRESS_DOCKERIGNORE,
)
from executors.backend.javascript.express.official import ExpressOfficialExecutor


class ExpressDockerExecutor(ExpressOfficialExecutor):
    """
    Executor that scaffolds an Express.js project with Docker support.

    Extends ExpressOfficialExecutor and adds:
      - Dockerfile       -- Production-ready multi-stage build
      - docker-compose.yml -- Dev service with hot-reload and volume mounts
      - .dockerignore

    Usage:
      docker compose up
    """

    def _add_docker_files(self, project_path: str) -> None:
        with open(os.path.join(project_path, 'Dockerfile'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_DOCKERFILE)

        with open(os.path.join(project_path, 'docker-compose.yml'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_DOCKER_COMPOSE)

        with open(os.path.join(project_path, '.dockerignore'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_DOCKERIGNORE)

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        result = super().execute_creation_commands(**kwargs)
        if not result.success:
            return result

        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        project_path = os.path.join(self.current_folder, directory_name)

        self._update_status('[bold blue]Adding Docker files...[/bold blue]')
        self._add_docker_files(project_path)

        self.console.print(
            f"[bold green]Express + Docker project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        batteries = [b.__class__.__name__ for b in self.batteries]
        batteries_note = (
            f'\nBatteries included: {", ".join(batteries)}\n' if batteries else ''
        )
        return (
            f'# {project_name}\n\n'
            'An Express.js + Docker project scaffolded with dev-scaffolder.\n'
            f'{batteries_note}\n'
            '## Requirements\n\n'
            '- Docker and Docker Compose\n\n'
            '## Run with Docker\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            'docker compose up\n'
            '```\n\n'
            '## Run locally\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            'npm install\n'
            'npm run dev\n'
            '```\n\n'
            'Server runs at http://localhost:3000\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'myproject') or 'myproject'
        directory_name = kwargs.get('directory_name', '') or project_name

        batteries_arg = kwargs.get('batteries', '') or ''
        if batteries_arg and not self.batteries:
            self.batteries = parse_express_batteries(batteries_arg)

        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
        )


def generate_express_docker_template(**kwargs) -> ExecutorResponseStatus:
    return ExpressDockerExecutor().run(**kwargs)


if __name__ == '__main__':
    args = ExpressDockerExecutor.build_arg_parser().parse_args()
    ExpressDockerExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
