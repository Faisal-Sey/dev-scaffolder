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
from typings.base import ExecutorResponseStatus
from utils.base import get_node_pm_commands
from constants.backend.javascript.nestjs.base import (
    NESTJS_PACKAGE_JSON,
    NESTJS_TSCONFIG,
    NESTJS_TSCONFIG_BUILD,
    NESTJS_NEST_CLI_JSON,
    NESTJS_MAIN_TS,
    NESTJS_REST_APP_MODULE_TS,
    NESTJS_APP_CONTROLLER_TS,
    NESTJS_APP_SERVICE_TS,
    NESTJS_APP_CONTROLLER_SPEC_TS,
    NESTJS_ITEMS_MODULE_TS,
    NESTJS_ITEMS_CONTROLLER_TS,
    NESTJS_ITEMS_SERVICE_TS,
    NESTJS_CREATE_ITEM_DTO_TS,
    NESTJS_UPDATE_ITEM_DTO_TS,
    NESTJS_GITIGNORE,
    NESTJS_ENV,
    NESTJS_ENV_EXAMPLE,
)


class NestJSRestAPIExecutor(BaseExecutor):
    """
    Executor that scaffolds a NestJS project with a full REST CRUD resource.

    Adds an ItemsModule with ItemsController and ItemsService providing
    GET/POST/PUT/DELETE /items endpoints with an in-memory data store.
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
        for cmd in [
            [npm, 'install'] + deps,
            [npm, 'install', '--save-dev'] + dev_deps,
        ]:
            result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True)
            if result.returncode != 0:
                self.console.print(f'[bold red]npm install failed: {result.stderr}[/bold red]')
                return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        os.makedirs(os.path.join(project_path, 'src', 'items', 'dto'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'test'), exist_ok=True)

        with open(os.path.join(project_path, 'src', 'main.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_MAIN_TS)

        with open(os.path.join(project_path, 'src', 'app.module.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_REST_APP_MODULE_TS)

        with open(os.path.join(project_path, 'src', 'app.controller.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_CONTROLLER_TS)

        with open(os.path.join(project_path, 'src', 'app.service.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_SERVICE_TS.replace('{project_name}', project_name))

        with open(os.path.join(project_path, 'src', 'app.controller.spec.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_CONTROLLER_SPEC_TS)

        with open(os.path.join(project_path, 'src', 'items', 'items.module.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_ITEMS_MODULE_TS)

        with open(os.path.join(project_path, 'src', 'items', 'items.controller.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_ITEMS_CONTROLLER_TS)

        with open(os.path.join(project_path, 'src', 'items', 'items.service.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_ITEMS_SERVICE_TS)

        with open(os.path.join(project_path, 'src', 'items', 'dto', 'create-item.dto.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_CREATE_ITEM_DTO_TS)

        with open(os.path.join(project_path, 'src', 'items', 'dto', 'update-item.dto.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_UPDATE_ITEM_DTO_TS)

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

        self._convert_package_manager(kwargs.get('package_manager', 'npm'), project_path)
        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name)

        self.console.print(
            f"[bold green]NestJS REST API project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A NestJS REST API project scaffolded with dev-scaffolder.\n\n'
            '## Endpoints\n\n'
            '| Method | Path | Description |\n'
            '|--------|------|-------------|\n'
            '| GET | / | Welcome message |\n'
            '| GET | /health | Health check |\n'
            '| GET | /items | List all items |\n'
            '| GET | /items/:id | Get item by id |\n'
            '| POST | /items | Create item |\n'
            '| PUT | /items/:id | Update item |\n'
            '| DELETE | /items/:id | Delete item |\n\n'
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
            'npm run start:dev\n'
            '```\n\n'
            'Server runs at http://localhost:3000\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'myproject') or 'myproject'
        directory_name = kwargs.get('directory_name', '') or project_name
        package_manager = kwargs.get('package_manager', 'npm') or 'npm'
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
        return parser


def generate_nestjs_rest_api_template(**kwargs) -> ExecutorResponseStatus:
    return NestJSRestAPIExecutor().run(**kwargs)


if __name__ == '__main__':
    args = NestJSRestAPIExecutor.build_arg_parser().parse_args()
    NestJSRestAPIExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        package_manager=args.package_manager,
    )