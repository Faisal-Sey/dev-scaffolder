import argparse
import os
import subprocess
import sys
from typing import List, cast

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from batteries.base import BaseBattery
from batteries.registry import parse_fastapi_batteries
from typings.base import ExecutorResponseStatus
from constants.backend.python.fastapi.base import (
    FASTAPI_MAIN_PY,
    FASTAPI_REQUIREMENTS,
    FASTAPI_ENV_EXAMPLE,
)
from utils.base import (
    check_or_create_venv,
    activate_venv,
    get_venv_python_executor,
    run_subprocess_command,
)


class FastAPIOfficialExecutor(BaseExecutor):
    """
    Executor that scaffolds a base FastAPI project.

    Project layout:
      {project_name}/
        app/
          __init__.py
          main.py       — FastAPI app with root and health endpoints
          routers/
            __init__.py
        requirements.txt
        .env.example
        README.md

    Supports optional batteries via the batteries prompt.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        check_or_create_venv()
        activate_venv()
        return get_venv_python_executor()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        for package in ['fastapi', 'uvicorn[standard]', 'python-dotenv']:
            command = [venv_python_executor, '-m', 'pip', 'install', package]
            if not run_subprocess_command(command):
                self.console.print(f'[bold red]Failed to install {package}[/bold red]')
                return ExecutorResponseStatus(success=False)
        self.console.print('[bold green]FastAPI dependencies installed[/bold green]')
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        os.makedirs(os.path.join(project_path, 'app', 'routers'), exist_ok=True)
        open(os.path.join(project_path, 'app', '__init__.py'), 'w').close()
        open(os.path.join(project_path, 'app', 'routers', '__init__.py'), 'w').close()

        with open(os.path.join(project_path, 'app', 'main.py'), 'w') as f:
            f.write(FASTAPI_MAIN_PY.format(project_name=project_name))

        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write(FASTAPI_REQUIREMENTS)

        with open(os.path.join(project_path, '.env.example'), 'w') as f:
            f.write(FASTAPI_ENV_EXAMPLE)

    def _freeze_requirements(self, venv_python_executor: str, project_path: str) -> None:
        result = subprocess.run(
            [venv_python_executor, '-m', 'pip', 'freeze'],
            capture_output=True, text=True, check=True,
        )
        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write(result.stdout)

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        project_path = cast(str, os.path.join(self.current_folder, directory_name))

        preparation = self.prepare_directory(project_path)
        if not preparation.success:
            return ExecutorResponseStatus(success=False)

        venv_python_executor = self.get_venv_environment()

        self._update_status('[bold blue]Installing FastAPI dependencies...[/bold blue]')
        install = self.install_dependencies(venv_python_executor)
        if not install.success:
            return ExecutorResponseStatus(success=False)

        self._update_status('[bold blue]Creating project structure...[/bold blue]')
        self._create_project_structure(project_path, project_name)

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f'[bold blue]Applying {battery_name}...[/bold blue]')
            result = battery.install(venv_python_executor)
            if not result.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, '')

        self._update_status('[bold blue]Updating requirements.txt...[/bold blue]')
        self._freeze_requirements(venv_python_executor, project_path)

        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name)

        self.console.print(
            f'[bold green]FastAPI project \'{project_name}\' created successfully![/bold green]'
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A FastAPI project scaffolded with dev-scaffolder.\n\n'
            '## Requirements\n\n'
            '- Python 3.10+\n\n'
            '## Setup\n\n'
            '```bash\n'
            'python -m venv venv\n'
            'source venv/bin/activate       # macOS / Linux\n'
            'venv\\Scripts\\activate          # Windows\n\n'
            'pip install -r requirements.txt\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'uvicorn app.main:app --reload\n'
            '```\n\n'
            'Open http://localhost:8000 in your browser.\n'
            'Interactive docs: http://localhost:8000/docs\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'test') or 'test'
        directory_name = kwargs.get('directory_name', '') or project_name

        batteries_arg = kwargs.get('batteries', '') or ''
        if batteries_arg and not self.batteries:
            self.batteries = parse_fastapi_batteries(batteries_arg)

        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject')
        parser.add_argument('--directory_name', type=str, default='myproject')
        parser.add_argument('--batteries', type=str, default='')
        return parser


def generate_fastapi_official_template(**kwargs) -> ExecutorResponseStatus:
    return FastAPIOfficialExecutor().run(**kwargs)


if __name__ == '__main__':
    args = FastAPIOfficialExecutor.build_arg_parser().parse_args()
    FastAPIOfficialExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
