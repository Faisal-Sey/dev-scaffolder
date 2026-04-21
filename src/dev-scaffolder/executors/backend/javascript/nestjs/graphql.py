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
    NESTJS_GRAPHQL_PACKAGE_JSON,
    NESTJS_TSCONFIG,
    NESTJS_TSCONFIG_BUILD,
    NESTJS_NEST_CLI_JSON,
    NESTJS_MAIN_TS,
    NESTJS_GRAPHQL_APP_MODULE_TS,
    NESTJS_APP_SERVICE_TS,
    NESTJS_APP_CONTROLLER_SPEC_TS,
    NESTJS_GRAPHQL_ITEM_MODEL_TS,
    NESTJS_GRAPHQL_ITEMS_SERVICE_TS,
    NESTJS_GRAPHQL_ITEMS_RESOLVER_TS,
    NESTJS_GRAPHQL_ITEMS_MODULE_TS,
    NESTJS_GITIGNORE,
    NESTJS_ENV,
    NESTJS_ENV_EXAMPLE,
)


class NestJSGraphQLExecutor(BaseExecutor):
    """
    Executor that scaffolds a NestJS project with GraphQL (code-first).

    Uses @nestjs/graphql + @nestjs/apollo with auto schema generation.
    Adds an ItemsModule with a resolver providing items/item queries and
    createItem mutation. Schema auto-written to src/schema.gql at startup.
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
        self._update_status('[bold blue]Installing NestJS + GraphQL dependencies...[/bold blue]')
        npm = self.get_venv_environment()
        deps = [
            '@apollo/server', '@as-integrations/express',
            '@nestjs/apollo', '@nestjs/common', '@nestjs/core',
            '@nestjs/graphql', '@nestjs/platform-express',
            'dotenv', 'graphql', 'reflect-metadata', 'rxjs',
        ]
        dev_deps = [
            '@nestjs/cli', '@nestjs/schematics', '@nestjs/testing',
            '@types/jest', '@types/node',
            'jest', 'ts-jest', 'ts-node', 'tslib', 'typescript',
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
        os.makedirs(os.path.join(project_path, 'src', 'items'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'test'), exist_ok=True)

        files = {
            'src/main.ts': NESTJS_MAIN_TS,
            'src/app.module.ts': NESTJS_GRAPHQL_APP_MODULE_TS,
            'src/app.controller.spec.ts': NESTJS_APP_CONTROLLER_SPEC_TS,
            'src/items/item.model.ts': NESTJS_GRAPHQL_ITEM_MODEL_TS,
            'src/items/items.service.ts': NESTJS_GRAPHQL_ITEMS_SERVICE_TS,
            'src/items/items.resolver.ts': NESTJS_GRAPHQL_ITEMS_RESOLVER_TS,
            'src/items/items.module.ts': NESTJS_GRAPHQL_ITEMS_MODULE_TS,
            'tsconfig.json': NESTJS_TSCONFIG,
            'tsconfig.build.json': NESTJS_TSCONFIG_BUILD,
            'nest-cli.json': NESTJS_NEST_CLI_JSON,
            '.gitignore': NESTJS_GITIGNORE,
            '.env': NESTJS_ENV,
            '.env.example': NESTJS_ENV_EXAMPLE,
        }

        for rel_path, content in files.items():
            full_path = os.path.join(project_path, rel_path)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        with open(os.path.join(project_path, 'src', 'app.service.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_SERVICE_TS.replace('{project_name}', project_name))

        with open(os.path.join(project_path, '.gitignore'), 'a', encoding='utf-8') as f:
            f.write('src/schema.gql\n')

    def _write_package_json(self, project_path: str, project_name: str) -> None:
        pkg = NESTJS_GRAPHQL_PACKAGE_JSON.replace('{project_name}', project_name)
        with open(os.path.join(project_path, 'package.json'), 'w', encoding='utf-8') as f:
            f.write(pkg)

    def _cleanup_battery_markers(self, project_path: str) -> None:
        fpath = os.path.join(project_path, 'src', 'main.ts')
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            for marker in ['// [BATTERY:IMPORTS]', '// [BATTERY:SETUP]']:
                content = content.replace(f'\n{marker}\n', '\n')
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
        self._cleanup_battery_markers(project_path)

        self._convert_package_manager(kwargs.get('package_manager', 'npm'), project_path)
        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name)

        self.console.print(
            f"[bold green]NestJS + GraphQL project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A NestJS + GraphQL (code-first) project scaffolded with dev-scaffolder.\n\n'
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
            'GraphQL Playground: http://localhost:3000/graphql\n\n'
            '## Example\n\n'
            '```graphql\n'
            'query { items { id name description } }\n'
            'mutation { createItem(name: "hello") { id name } }\n'
            '```\n'
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


def generate_nestjs_graphql_template(**kwargs) -> ExecutorResponseStatus:
    return NestJSGraphQLExecutor().run(**kwargs)


if __name__ == '__main__':
    args = NestJSGraphQLExecutor.build_arg_parser().parse_args()
    NestJSGraphQLExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        package_manager=args.package_manager,
    )