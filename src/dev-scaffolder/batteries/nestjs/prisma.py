import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import (
    NESTJS_PRISMA_SERVICE_TS,
    NESTJS_PRISMA_MODULE_TS,
    NESTJS_PRISMA_IMPORT,
    NESTJS_PRISMA_MODULE_IMPORT,
    NESTJS_PRISMA_SCHEMA,
)
from typings.base import ExecutorResponseStatus


class NestJSPrismaBattery(BaseBattery):
    """
    Battery that adds Prisma ORM to a NestJS app.

    Installs 'prisma' and '@prisma/client', writes prisma/schema.prisma
    (SQLite by default), runs prisma generate, and creates a global
    PrismaModule with PrismaService that extends PrismaClient.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        npm = shutil.which('npm') or 'npm'
        npx = shutil.which('npx') or 'npx'

        result = subprocess.run(
            [npm, 'install', 'prisma', '@prisma/client'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f'[bold red]Failed to install prisma: {result.stderr}[/bold red]'
            )
            return ExecutorResponseStatus(success=False)

        prisma_dir = os.path.join(project_path, 'prisma')
        os.makedirs(prisma_dir, exist_ok=True)
        with open(os.path.join(prisma_dir, 'schema.prisma'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_PRISMA_SCHEMA)

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

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        prisma_dir = os.path.join(project_path, 'src', 'prisma')
        os.makedirs(prisma_dir, exist_ok=True)

        with open(os.path.join(prisma_dir, 'prisma.service.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_PRISMA_SERVICE_TS)

        with open(os.path.join(prisma_dir, 'prisma.module.ts'), 'w', encoding='utf-8') as f:
            f.write(NESTJS_PRISMA_MODULE_TS)

        app_module = os.path.join(project_path, 'src', 'app.module.ts')
        try:
            with open(app_module, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{NESTJS_PRISMA_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '    // [BATTERY:MODULE_IMPORTS]',
                f'{NESTJS_PRISMA_MODULE_IMPORT}    // [BATTERY:MODULE_IMPORTS]',
            )
            with open(app_module, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {app_module}[/bold red]')
            return

        env_example = os.path.join(project_path, '.env.example')
        try:
            with open(env_example, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'DATABASE_URL' not in content:
                content += 'DB_PROVIDER=sqlite\nDATABASE_URL=file:./dev.db\n'
            with open(env_example, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            pass