import argparse
import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from typings.base import ExecutorResponseStatus
from constants.backend.go.echo.base import (
    ECHO_GORM_GO_MOD,
    ECHO_GORM_MAIN_GO,
    ECHO_GITIGNORE,
    ECHO_GORM_ENV,
    ECHO_GORM_ENV_EXAMPLE,
)


class EchoGormExecutor(BaseExecutor):
    """Scaffolds an Echo v4 project with GORM and SQLite."""

    def get_venv_environment(self) -> str:
        go = shutil.which('go')
        if not go:
            raise RuntimeError('go not found in PATH. Please install Go.')
        return go

    def install_dependencies(self, go_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def _tidy_dependencies(self, project_path: str) -> ExecutorResponseStatus:
        self._update_status('[bold blue]Downloading Go dependencies...[/bold blue]')
        result = subprocess.run(
            [self.get_venv_environment(), 'mod', 'tidy'],
            cwd=project_path, capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]go mod tidy failed:[/bold red]\n{result.stderr}')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        os.makedirs(project_path, exist_ok=True)

        def write(path, content):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.replace('{project_name}', project_name))

        write(os.path.join(project_path, 'go.mod'), ECHO_GORM_GO_MOD)
        write(os.path.join(project_path, 'main.go'), ECHO_GORM_MAIN_GO)
        write(os.path.join(project_path, '.gitignore'), ECHO_GITIGNORE)
        write(os.path.join(project_path, '.env'), ECHO_GORM_ENV)
        write(os.path.join(project_path, '.env.example'), ECHO_GORM_ENV_EXAMPLE)

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        project_path = os.path.join(self.current_folder, directory_name)

        if not self.prepare_directory(project_path).success:
            return ExecutorResponseStatus(success=False)

        self._update_status('[bold blue]Creating project structure...[/bold blue]')
        self._create_project_structure(project_path, project_name)

        if not self._tidy_dependencies(project_path).success:
            return ExecutorResponseStatus(success=False)

        self._write_readme(project_path, project_name=project_name)
        self.console.print(
            f"[bold green]Echo GORM project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'An Echo v4 project with GORM and SQLite scaffolded with dev-scaffolder.\n\n'
            '## Endpoints\n\n'
            '| Method | Path | Description |\n'
            '|--------|------|-------------|\n'
            '| GET | /api/items | List all items |\n'
            '| GET | /api/items/:id | Get item by ID |\n'
            '| POST | /api/items | Create item |\n'
            '| PUT | /api/items/:id | Update item |\n'
            '| DELETE | /api/items/:id | Delete item |\n\n'
            '## Setup\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            '# Edit DATABASE_URL in .env (default: in-memory SQLite)\n'
            'go run .\n'
            '```\n\n'
            '> Note: GORM with SQLite requires CGO. Ensure gcc is installed.\n\n'
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


def generate_echo_gorm_template(**kwargs) -> ExecutorResponseStatus:
    return EchoGormExecutor().run(**kwargs)


if __name__ == '__main__':
    args = EchoGormExecutor.build_arg_parser().parse_args()
    EchoGormExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
    )
