import argparse
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
    FASTIFY_PRISMA_SCHEMA,
    FASTIFY_PRISMA_DB_JS,
    FASTIFY_PRISMA_IMPORT,
)


class FastifyPrismaExecutor(BaseExecutor):
    """
    Executor that scaffolds a Fastify project with Prisma ORM pre-configured.

    Project layout:
      {project_name}/
        src/
          index.js
          app.js          -- Imports PrismaClient singleton from src/db.js
          db.js           -- PrismaClient singleton
          routes/
            index.js
        prisma/
          schema.prisma   -- SQLite by default; change DB_PROVIDER/DATABASE_URL in .env
        package.json
        .env
        .env.example
        .gitignore
        README.md

    After scaffolding, define your models in prisma/schema.prisma then run:
      npx prisma db push      -- sync schema to database (dev)
      npx prisma migrate dev  -- create a migration (production workflow)
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
        self._update_status('[bold blue]Installing Fastify + Prisma dependencies...[/bold blue]')
        npm = self.get_venv_environment()
        npx = __import__('shutil').which('npx') or 'npx'

        for cmd in [
            [npm, 'install', 'fastify', 'dotenv', 'prisma', '@prisma/client'],
            [npm, 'install', '--save-dev', 'nodemon'],
        ]:
            result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True)
            if result.returncode != 0:
                self.console.print(
                    f'[bold red]npm install failed: {result.stderr}[/bold red]'
                )
                return ExecutorResponseStatus(success=False)

        # Write schema before generating the client
        prisma_dir = os.path.join(project_path, 'prisma')
        os.makedirs(prisma_dir, exist_ok=True)
        with open(os.path.join(prisma_dir, 'schema.prisma'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_PRISMA_SCHEMA)

        result = subprocess.run(
            [npx, 'prisma', 'generate'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f'[bold red]prisma generate failed: {result.stderr}[/bold red]'
            )
            return ExecutorResponseStatus(success=False)

        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        os.makedirs(os.path.join(project_path, 'src', 'routes'), exist_ok=True)

        with open(os.path.join(project_path, 'src', 'index.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_INDEX_JS)

        # Inject the Prisma import above the battery marker
        app_js_content = FASTIFY_APP_JS.replace(
            '// [BATTERY:IMPORTS]',
            f'{FASTIFY_PRISMA_IMPORT}// [BATTERY:IMPORTS]',
        )
        with open(os.path.join(project_path, 'src', 'app.js'), 'w', encoding='utf-8') as f:
            f.write(app_js_content)

        with open(os.path.join(project_path, 'src', 'db.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_PRISMA_DB_JS)

        with open(os.path.join(project_path, 'src', 'routes', 'index.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_ROUTES_INDEX_JS.replace('{project_name}', project_name))

        with open(os.path.join(project_path, '.gitignore'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_GITIGNORE)

        env_content = FASTIFY_ENV + 'DB_PROVIDER=sqlite\nDATABASE_URL=file:./dev.db\n'
        with open(os.path.join(project_path, '.env'), 'w', encoding='utf-8') as f:
            f.write(env_content)

        env_example_content = FASTIFY_ENV_EXAMPLE + 'DB_PROVIDER=sqlite\nDATABASE_URL=file:./dev.db\n'
        with open(os.path.join(project_path, '.env.example'), 'w', encoding='utf-8') as f:
            f.write(env_example_content)

    def _write_package_json(self, project_path: str, project_name: str) -> None:
        pkg_content = FASTIFY_PACKAGE_JSON.replace('{project_name}', project_name)
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
            f"[bold green]Fastify + Prisma project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Fastify + Prisma project scaffolded with dev-scaffolder.\n\n'
            '## Requirements\n\n'
            '- Node.js 18+\n'
            '- npm\n\n'
            '## Setup\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            'npm install\n'
            '```\n\n'
            '## Database\n\n'
            'SQLite is configured by default. '
            'Edit `DB_PROVIDER` and `DATABASE_URL` in `.env` to switch databases.\n\n'
            '```bash\n'
            '# Apply schema to the database\n'
            'npx prisma db push\n\n'
            '# Or use migrations (production workflow)\n'
            'npx prisma migrate dev\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'npm run dev\n'
            '```\n\n'
            'Server runs at http://localhost:3000\n'
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


def generate_fastify_prisma_template(**kwargs) -> ExecutorResponseStatus:
    return FastifyPrismaExecutor().run(**kwargs)


if __name__ == '__main__':
    args = FastifyPrismaExecutor.build_arg_parser().parse_args()
    FastifyPrismaExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        batteries=args.batteries,
    )
