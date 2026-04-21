import argparse
import os
import re
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from typings.base import ExecutorResponseStatus
from constants.backend.rust.rocket.base import (
    ROCKET_CARGO_TOML,
    ROCKET_TESTING_MAIN_RS,
    ROCKET_TOML,
    ROCKET_GITIGNORE,
    ROCKET_ENV,
    ROCKET_ENV_EXAMPLE,
)


def _crate_name(project_name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '-', project_name) or 'my-project'


class RocketTestingExecutor(BaseExecutor):
    """Scaffolds a Rocket 0.5 project with built-in integration tests."""

    def get_venv_environment(self) -> str:
        cargo = shutil.which('cargo')
        if not cargo:
            raise RuntimeError('cargo not found in PATH. Please install Rust.')
        return cargo

    def install_dependencies(self, cargo_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def _fetch_dependencies(self, project_path: str) -> ExecutorResponseStatus:
        self._update_status('[bold blue]Fetching Cargo dependencies...[/bold blue]')
        result = subprocess.run(
            [self.get_venv_environment(), 'fetch'],
            cwd=project_path, capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]cargo fetch failed:[/bold red]\n{result.stderr}')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        src = os.path.join(project_path, 'src')
        os.makedirs(src, exist_ok=True)

        def write(path, content):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.replace('{project_name}', project_name))

        write(os.path.join(project_path, 'Cargo.toml'), ROCKET_CARGO_TOML)
        write(os.path.join(src, 'main.rs'), ROCKET_TESTING_MAIN_RS)
        write(os.path.join(project_path, 'Rocket.toml'), ROCKET_TOML)
        write(os.path.join(project_path, '.gitignore'), ROCKET_GITIGNORE)
        write(os.path.join(project_path, '.env'), ROCKET_ENV)
        write(os.path.join(project_path, '.env.example'), ROCKET_ENV_EXAMPLE)

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        project_path = os.path.join(self.current_folder, directory_name)

        if not self.prepare_directory(project_path).success:
            return ExecutorResponseStatus(success=False)

        self._update_status('[bold blue]Creating project structure...[/bold blue]')
        self._create_project_structure(project_path, _crate_name(project_name))

        if not self._fetch_dependencies(project_path).success:
            return ExecutorResponseStatus(success=False)

        self._write_readme(project_path, project_name=project_name)
        self.console.print(
            f"[bold green]Rocket testing project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Rocket 0.5 project with integration tests scaffolded with dev-scaffolder.\n\n'
            '## Run Tests\n\n'
            '```bash\n'
            'cargo test\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'cargo run\n'
            '```\n\n'
            'Server runs at http://localhost:8080\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'my-project') or 'my-project'
        directory_name = kwargs.get('directory_name', '') or project_name
        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='my-project')
        parser.add_argument('--directory_name', type=str, default='my-project')
        return parser


def generate_rocket_testing_template(**kwargs) -> ExecutorResponseStatus:
    return RocketTestingExecutor().run(**kwargs)


if __name__ == '__main__':
    args = RocketTestingExecutor.build_arg_parser().parse_args()
    RocketTestingExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
    )