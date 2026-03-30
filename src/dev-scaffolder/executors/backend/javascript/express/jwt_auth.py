import argparse
import os
import subprocess
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from batteries.base import BaseBattery
from batteries.registry import parse_express_batteries
from typings.base import ExecutorResponseStatus
from constants.backend.javascript.express.base import (
    EXPRESS_JWT_PACKAGE_JSON,
    EXPRESS_JWT_APP_JS,
    EXPRESS_JWT_AUTH_MIDDLEWARE_JS,
    EXPRESS_JWT_AUTH_ROUTES_JS,
    EXPRESS_ROUTES_INDEX_JS,
    EXPRESS_INDEX_JS,
    EXPRESS_GITIGNORE,
    EXPRESS_ENV_EXAMPLE,
    EXPRESS_JWT_ENV_EXAMPLE,
)


class ExpressJWTAuthExecutor(BaseExecutor):
    """
    Executor that scaffolds an Express.js project with JWT authentication.

    Project layout:
      {project_name}/
        src/
          index.js
          app.js              -- Mounts auth router at /auth
          middleware/
            auth.js           -- authenticateToken middleware
          routes/
            index.js          -- Root and /health routes
            auth.js           -- /register, /login, /refresh, /me routes
        package.json
        .env.example
        .gitignore
        README.md

    Auth endpoints:
      POST /auth/register  -- Create account
      POST /auth/login     -- Get access + refresh tokens
      POST /auth/refresh   -- Exchange refresh token for new access token
      GET  /auth/me        -- Protected: returns current user
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
        self._update_status('[bold blue]Installing Express + JWT dependencies...[/bold blue]')
        for cmd in [
            [shutil.which('npm') or 'npm', 'install', 'express', 'dotenv', 'jsonwebtoken', 'bcryptjs'],
            [shutil.which('npm') or 'npm', 'install', '--save-dev', 'nodemon'],
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
        os.makedirs(os.path.join(project_path, 'src', 'middleware'), exist_ok=True)

        with open(os.path.join(project_path, 'src', 'index.js'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_INDEX_JS)

        with open(os.path.join(project_path, 'src', 'app.js'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_JWT_APP_JS)

        with open(os.path.join(project_path, 'src', 'middleware', 'auth.js'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_JWT_AUTH_MIDDLEWARE_JS)

        with open(os.path.join(project_path, 'src', 'routes', 'index.js'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_ROUTES_INDEX_JS.replace('{project_name}', project_name))

        with open(os.path.join(project_path, 'src', 'routes', 'auth.js'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_JWT_AUTH_ROUTES_JS)

        with open(os.path.join(project_path, '.gitignore'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_GITIGNORE)

        with open(os.path.join(project_path, '.env.example'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_JWT_ENV_EXAMPLE)

        env_path = os.path.join(project_path, '.env')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(EXPRESS_JWT_ENV_EXAMPLE)

    def _write_package_json(self, project_path: str, project_name: str) -> None:
        pkg_content = EXPRESS_JWT_PACKAGE_JSON.replace('{project_name}', project_name)
        with open(os.path.join(project_path, 'package.json'), 'w', encoding='utf-8') as f:
            f.write(pkg_content)

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
            for marker in ['// [BATTERY:IMPORTS]', '// [BATTERY:MIDDLEWARE]']:
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
            f"[bold green]Express + JWT Auth project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'An Express.js + JWT Auth project scaffolded with dev-scaffolder.\n\n'
            '## Requirements\n\n'
            '- Node.js 18+\n'
            '- npm\n\n'
            '## Setup\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            '# Edit .env and set strong JWT_SECRET and JWT_REFRESH_SECRET values\n'
            'npm install\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'npm run dev\n'
            '```\n\n'
            '## Auth Endpoints\n\n'
            '| Method | Path             | Description                  |\n'
            '|--------|------------------|------------------------------|\n'
            '| POST   | /auth/register   | Create a new account         |\n'
            '| POST   | /auth/login      | Get access + refresh tokens  |\n'
            '| POST   | /auth/refresh    | Refresh the access token     |\n'
            '| GET    | /auth/me         | Get current user (protected) |\n\n'
            'Protected routes require: `Authorization: Bearer <accessToken>`\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'myproject') or 'myproject'
        directory_name = kwargs.get('directory_name', '') or project_name

        package_manager = kwargs.get('package_manager', 'npm') or 'npm'
        batteries_arg = kwargs.get('batteries', '') or ''
        if batteries_arg and not self.batteries:
            self.batteries = parse_express_batteries(batteries_arg)

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


def generate_express_jwt_auth_template(**kwargs) -> ExecutorResponseStatus:
    return ExpressJWTAuthExecutor().run(**kwargs)


if __name__ == '__main__':
    args = ExpressJWTAuthExecutor.build_arg_parser().parse_args()
    ExpressJWTAuthExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
