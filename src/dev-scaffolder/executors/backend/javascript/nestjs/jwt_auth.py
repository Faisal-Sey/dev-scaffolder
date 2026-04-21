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
    NESTJS_JWT_PACKAGE_JSON,
    NESTJS_TSCONFIG,
    NESTJS_TSCONFIG_BUILD,
    NESTJS_NEST_CLI_JSON,
    NESTJS_MAIN_TS,
    NESTJS_JWT_APP_MODULE_TS,
    NESTJS_APP_CONTROLLER_TS,
    NESTJS_APP_SERVICE_TS,
    NESTJS_APP_CONTROLLER_SPEC_TS,
    NESTJS_AUTH_MODULE_TS,
    NESTJS_AUTH_SERVICE_TS,
    NESTJS_AUTH_CONTROLLER_TS,
    NESTJS_JWT_STRATEGY_TS,
    NESTJS_JWT_AUTH_GUARD_TS,
    NESTJS_USERS_MODULE_TS,
    NESTJS_USERS_SERVICE_TS,
    NESTJS_GITIGNORE,
    NESTJS_ENV,
    NESTJS_JWT_ENV_EXAMPLE,
)


class NestJSJwtAuthExecutor(BaseExecutor):
    """
    Executor that scaffolds a NestJS project with JWT authentication.

    Adds AuthModule (register/login endpoints) and UsersModule backed by an
    in-memory store. Uses @nestjs/jwt + passport-jwt for token verification.
    Decorate protected routes with @UseGuards(JwtAuthGuard).
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
        self._update_status('[bold blue]Installing NestJS JWT auth dependencies...[/bold blue]')
        npm = self.get_venv_environment()
        deps = [
            '@nestjs/common', '@nestjs/core', '@nestjs/platform-express',
            '@nestjs/jwt', '@nestjs/passport',
            'bcryptjs', 'dotenv', 'passport', 'passport-jwt',
            'reflect-metadata', 'rxjs',
        ]
        dev_deps = [
            '@nestjs/cli', '@nestjs/schematics', '@nestjs/testing',
            '@types/bcryptjs', '@types/express', '@types/jest',
            '@types/node', '@types/passport-jwt', '@types/supertest',
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
        for d in ['src/auth', 'src/users', 'test']:
            os.makedirs(os.path.join(project_path, d), exist_ok=True)

        files = {
            'src/main.ts': NESTJS_MAIN_TS,
            'src/app.module.ts': NESTJS_JWT_APP_MODULE_TS,
            'src/app.controller.ts': NESTJS_APP_CONTROLLER_TS,
            'src/app.controller.spec.ts': NESTJS_APP_CONTROLLER_SPEC_TS,
            'src/auth/auth.module.ts': NESTJS_AUTH_MODULE_TS,
            'src/auth/auth.service.ts': NESTJS_AUTH_SERVICE_TS,
            'src/auth/auth.controller.ts': NESTJS_AUTH_CONTROLLER_TS,
            'src/auth/jwt.strategy.ts': NESTJS_JWT_STRATEGY_TS,
            'src/auth/jwt-auth.guard.ts': NESTJS_JWT_AUTH_GUARD_TS,
            'src/users/users.module.ts': NESTJS_USERS_MODULE_TS,
            'src/users/users.service.ts': NESTJS_USERS_SERVICE_TS,
            'tsconfig.json': NESTJS_TSCONFIG,
            'tsconfig.build.json': NESTJS_TSCONFIG_BUILD,
            'nest-cli.json': NESTJS_NEST_CLI_JSON,
            '.gitignore': NESTJS_GITIGNORE,
            '.env': NESTJS_ENV,
            '.env.example': NESTJS_JWT_ENV_EXAMPLE,
        }

        for rel_path, content in files.items():
            full_path = os.path.join(project_path, rel_path)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        with open(os.path.join(project_path, 'src', 'app.service.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_APP_SERVICE_TS.replace('{project_name}', project_name))

    def _write_package_json(self, project_path: str, project_name: str) -> None:
        pkg = NESTJS_JWT_PACKAGE_JSON.replace('{project_name}', project_name)
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
            f"[bold green]NestJS JWT auth project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A NestJS project with JWT authentication scaffolded with dev-scaffolder.\n\n'
            '## Auth Endpoints\n\n'
            '| Method | Path | Description |\n'
            '|--------|------|-------------|\n'
            '| POST | /auth/register | Register a new user |\n'
            '| POST | /auth/login | Login, returns access_token |\n\n'
            '## Protected routes\n\n'
            'Use `@UseGuards(JwtAuthGuard)` on any controller or route handler.\n'
            'Send `Authorization: Bearer <token>` in the request header.\n\n'
            '## Requirements\n\n'
            '- Node.js 18+\n'
            '- npm\n\n'
            '## Setup\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            '# Edit JWT_SECRET in .env\n'
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


def generate_nestjs_jwt_auth_template(**kwargs) -> ExecutorResponseStatus:
    return NestJSJwtAuthExecutor().run(**kwargs)


if __name__ == '__main__':
    args = NestJSJwtAuthExecutor.build_arg_parser().parse_args()
    NestJSJwtAuthExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        package_manager=args.package_manager,
    )