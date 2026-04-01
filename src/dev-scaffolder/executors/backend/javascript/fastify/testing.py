import argparse
import json
import os
import subprocess
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from batteries.base import BaseBattery
from batteries.registry import parse_fastify_batteries
from typings.base import ExecutorResponseStatus
from utils.base import get_node_pm_commands
from constants.backend.javascript.fastify.base import (
    FASTIFY_PACKAGE_JSON,
    FASTIFY_INDEX_JS,
    FASTIFY_APP_JS,
    FASTIFY_ROUTES_INDEX_JS,
    FASTIFY_GITIGNORE,
    FASTIFY_ENV,
    FASTIFY_ENV_EXAMPLE,
    FASTIFY_EXAMPLE_TEST_JS,
)


class FastifyTestingExecutor(BaseExecutor):
    """
    Executor that scaffolds a Fastify project with Jest pre-configured.

    Project layout:
      {project_name}/
        src/
          index.js
          app.js
          routes/
            index.js
        tests/
          app.test.js   -- Example tests using fastify.inject()
        package.json    -- "test" script wired to jest
        .env
        .env.example
        .gitignore
        README.md

    Fastify's built-in inject() method is used for testing — no extra HTTP
    client library required.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        import shutil
        npm = shutil.which('npm')
        if not npm:
            raise RuntimeError('npm not found in PATH. Please install Node.js.')
        return npm

    def install_dependencies(self, project_path: str) -> ExecutorResponseStatus:
        self._update_status('[bold blue]Installing Fastify + Jest dependencies...[/bold blue]')
        npm = self.get_venv_environment()
        for cmd in [
            [npm, 'install', 'fastify', 'dotenv'],
            [npm, 'install', '--save-dev', 'nodemon', 'jest'],
        ]:
            result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True)
            if result.returncode != 0:
                self.console.print(
                    f'[bold red]npm install failed: {result.stderr}[/bold red]'
                )
                return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        os.makedirs(os.path.join(project_path, 'src', 'routes'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'tests'), exist_ok=True)

        with open(os.path.join(project_path, 'src', 'index.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_INDEX_JS)

        with open(os.path.join(project_path, 'src', 'app.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_APP_JS)

        with open(os.path.join(project_path, 'src', 'routes', 'index.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_ROUTES_INDEX_JS.replace('{project_name}', project_name))

        with open(os.path.join(project_path, 'tests', 'app.test.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_EXAMPLE_TEST_JS)

        with open(os.path.join(project_path, '.gitignore'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_GITIGNORE)

        with open(os.path.join(project_path, '.env'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_ENV)

        with open(os.path.join(project_path, '.env.example'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_ENV_EXAMPLE)

    def _write_package_json(self, project_path: str, project_name: str) -> None:
        pkg_content = FASTIFY_PACKAGE_JSON.replace('{project_name}', project_name)
        pkg = json.loads(pkg_content)
        pkg.setdefault('scripts', {})['test'] = 'jest'
        pkg['jest'] = {'testEnvironment': 'node'}
        with open(os.path.join(project_path, 'package.json'), 'w', encoding='utf-8') as f:
            json.dump(pkg, f, indent=2)
            f.write('\n')

    def _convert_package_manager(self, pm: str, project_path: str) -> None:
        if not pm or pm == 'npm':
            return
        lock = os.path.join(project_path, 'package-lock.json')
        if os.path.exists(lock):
            os.remove(lock)
        self._update_status(f'[bold blue]Switching to {pm}...[/bold blue]')
        pm_cmds = get_node_pm_commands(pm)
        subprocess.run(pm_cmds['install'], cwd=project_path, capture_output=True, text=True)

    def _cleanup_battery_markers(self, project_path: str) -> None:
        app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
            for marker in ['// [BATTERY:IMPORTS]', '// [BATTERY:PLUGINS]']:
                content = content.replace(f'\n{marker}\n', '\n')
            with open(app_js, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            pass

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        project_path = os.path.join(self.current_folder, directory_name)

        preparation = self.prepare_directory(project_path)
        if not preparation.success:
            return ExecutorResponseStatus(success=False)

        self._update_status('[bold blue]Initialising npm project...[/bold blue]')
        result = subprocess.run(
            [self.get_venv_environment(), 'init', '-y'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]npm init failed: {result.stderr}[/bold red]')
            return ExecutorResponseStatus(success=False)

        install = self.install_dependencies(project_path)
        if not install.success:
            return ExecutorResponseStatus(success=False)

        self._update_status('[bold blue]Creating project structure...[/bold blue]')
        self._create_project_structure(project_path, project_name)
        self._write_package_json(project_path, project_name)

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f'[bold blue]Applying {battery_name}...[/bold blue]')
            result = battery.install(project_path)
            if not result.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, '')

        self._cleanup_battery_markers(project_path)

        self._convert_package_manager(kwargs.get('package_manager', 'npm'), project_path)
        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name)

        self.console.print(
            f"[bold green]Fastify + Jest project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Fastify project with Jest testing scaffolded with dev-scaffolder.\n\n'
            '## Requirements\n\n'
            '- Node.js 18+\n'
            '- npm\n\n'
            '## Setup\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            'npm install\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'npm run dev\n'
            '```\n\n'
            '## Test\n\n'
            '```bash\n'
            'npm test\n'
            '```\n\n'
            'Tests use `fastify.inject()` — no running server needed.\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'myproject') or 'myproject'
        directory_name = kwargs.get('directory_name', '') or project_name
        package_manager = kwargs.get('package_manager', 'npm') or 'npm'
        batteries_arg = kwargs.get('batteries', '') or ''
        if batteries_arg and not self.batteries:
            self.batteries = parse_fastify_batteries(batteries_arg)

        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
            package_manager=package_manager,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject')
        parser.add_argument('--directory_name', type=str, default='myproject')
        parser.add_argument('--package_manager', type=str, default='npm')
        parser.add_argument('--batteries', type=str, default='')
        return parser


def generate_fastify_testing_template(**kwargs) -> ExecutorResponseStatus:
    return FastifyTestingExecutor().run(**kwargs)


if __name__ == '__main__':
    args = FastifyTestingExecutor.build_arg_parser().parse_args()
    FastifyTestingExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
