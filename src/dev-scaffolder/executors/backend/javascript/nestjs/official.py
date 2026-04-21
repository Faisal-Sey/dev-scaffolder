import argparse
import os
import shutil
import subprocess
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from batteries.base import BaseBattery
from batteries.registry import parse_nestjs_batteries
from typings.base import ExecutorResponseStatus
from utils.base import get_node_pm_commands
from constants.backend.javascript.nestjs.base import (
    NESTJS_PACKAGE_JSON,
    NESTJS_TSCONFIG,
    NESTJS_TSCONFIG_BUILD,
    NESTJS_NEST_CLI_JSON,
    NESTJS_MAIN_TS,
    NESTJS_APP_MODULE_TS,
    NESTJS_APP_CONTROLLER_TS,
    NESTJS_APP_SERVICE_TS,
    NESTJS_APP_CONTROLLER_SPEC_TS,
    NESTJS_GITIGNORE,
    NESTJS_ENV,
    NESTJS_ENV_EXAMPLE,
)


class NestJSOfficialExecutor(BaseExecutor):
    """
    Executor that scaffolds a base NestJS project.

    Project layout:
      {project_name}/
        src/
          main.ts           -- Bootstrap entry point
          app.module.ts     -- Root application module
          app.controller.ts -- Root controller (GET / and GET /health)
          app.service.ts    -- Root service
          app.controller.spec.ts
        test/
        tsconfig.json
        tsconfig.build.json
        nest-cli.json
        package.json
        .env
        .env.example
        .gitignore
        README.md

    Requires Node.js and npm to be installed and available in PATH.
    Supports optional batteries via the batteries argument.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        npm = shutil.which('npm')
        if not npm:
            raise RuntimeError('npm not found in PATH. Please install Node.js.')
        return npm

    def install_dependencies(self, project_path: str) -> ExecutorResponseStatus:
        self._update_status('[bold blue]Installing NestJS dependencies...[/bold blue]')
        npm = self.get_venv_environment()
        deps = [
            '@nestjs/common', '@nestjs/core', '@nestjs/platform-express',
            'dotenv', 'reflect-metadata', 'rxjs',
        ]
        dev_deps = [
            '@nestjs/cli', '@nestjs/schematics', '@nestjs/testing',
            '@types/express', '@types/jest', '@types/node', '@types/supertest',
            'jest', 'source-map-support', 'supertest',
            'ts-jest', 'ts-node', 'tslib', 'typescript',
        ]
        result = subprocess.run(
            [npm, 'install'] + deps,
            cwd=project_path, capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]npm install failed: {result.stderr}[/bold red]')
            return ExecutorResponseStatus(success=False)
        result = subprocess.run(
            [npm, 'install', '--save-dev'] + dev_deps,
            cwd=project_path, capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]npm install (dev) failed: {result.stderr}[/bold red]')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'test'), exist_ok=True)

        with open(os.path.join(project_path, 'src', 'main.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_MAIN_TS)

        with open(os.path.join(project_path, 'src', 'app.module.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_MODULE_TS)

        with open(os.path.join(project_path, 'src', 'app.controller.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_CONTROLLER_TS)

        with open(os.path.join(project_path, 'src', 'app.service.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_SERVICE_TS.replace('{project_name}', project_name))

        with open(os.path.join(project_path, 'src', 'app.controller.spec.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_CONTROLLER_SPEC_TS)

        with open(os.path.join(project_path, 'tsconfig.json'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_TSCONFIG)

        with open(os.path.join(project_path, 'tsconfig.build.json'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_TSCONFIG_BUILD)

        with open(os.path.join(project_path, 'nest-cli.json'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_NEST_CLI_JSON)

        with open(os.path.join(project_path, '.gitignore'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_GITIGNORE)

        with open(os.path.join(project_path, '.env'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_ENV)

        with open(os.path.join(project_path, '.env.example'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_ENV_EXAMPLE)

    def _write_package_json(self, project_path: str, project_name: str) -> None:
        pkg = NESTJS_PACKAGE_JSON.replace('{project_name}', project_name)
        with open(os.path.join(project_path, 'package.json'), 'w', encoding='utf-8') as f:
            f.write(pkg)

    def _cleanup_battery_markers(self, project_path: str) -> None:
        for fname in ['src/main.ts', 'src/app.module.ts']:
            fpath = os.path.join(project_path, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                for marker in [
                    '// [BATTERY:IMPORTS]',
                    '// [BATTERY:SETUP]',
                    '// [BATTERY:MODULE_IMPORTS]',
                ]:
                    content = content.replace(f'\n{marker}\n', '\n')
                    content = content.replace(f'    {marker}\n', '')
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
            except FileNotFoundError:
                pass

    def _convert_package_manager(self, pm: str, project_path: str) -> None:
        if not pm or pm == 'npm':
            return
        lock = os.path.join(project_path, 'package-lock.json')
        if os.path.exists(lock):
            os.remove(lock)
        self._update_status(f'[bold blue]Switching to {pm}...[/bold blue]')
        pm_cmds = get_node_pm_commands(pm)
        subprocess.run(pm_cmds['install'], cwd=project_path, capture_output=True, text=True)

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
            cwd=project_path, capture_output=True, text=True,
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
            f"[bold green]NestJS project '{project_name}' created successfully![/bold green]"
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
            'A NestJS project scaffolded with dev-scaffolder.\n'
            f'{batteries_note}\n'
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
            '# Development (with auto-reload)\n'
            'npm run start:dev\n\n'
            '# Build\n'
            'npm run build\n\n'
            '# Production\n'
            'npm run start:prod\n'
            '```\n\n'
            '## Test\n\n'
            '```bash\n'
            'npm test\n'
            '```\n\n'
            'Server runs at http://localhost:3000\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'myproject') or 'myproject'
        directory_name = kwargs.get('directory_name', '') or project_name
        package_manager = kwargs.get('package_manager', 'npm') or 'npm'
        batteries_arg = kwargs.get('batteries', '') or ''
        if batteries_arg and not self.batteries:
            self.batteries = parse_nestjs_batteries(batteries_arg)
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


def generate_nestjs_official_template(**kwargs) -> ExecutorResponseStatus:
    return NestJSOfficialExecutor().run(**kwargs)


if __name__ == '__main__':
    args = NestJSOfficialExecutor.build_arg_parser().parse_args()
    NestJSOfficialExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        package_manager=args.package_manager,
    )