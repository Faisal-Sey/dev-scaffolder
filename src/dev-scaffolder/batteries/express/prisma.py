import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.express.base import (
    EXPRESS_PRISMA_SCHEMA,
    EXPRESS_PRISMA_DB_JS,
    EXPRESS_PRISMA_IMPORT,
)
from typings.base import ExecutorResponseStatus


class ExpressPrismaBattery(BaseBattery):
    """
    Battery that adds Prisma ORM to an Express app.

    Installs 'prisma' and '@prisma/client', writes prisma/schema.prisma
    (SQLite by default — change DB_PROVIDER and DATABASE_URL in .env),
    generates the Prisma client, and creates src/db.js with a PrismaClient
    singleton that is imported into src/app.js.

    After scaffolding, define your models in prisma/schema.prisma then run:
      npx prisma db push     -- sync schema to database (dev)
      npx prisma migrate dev -- create a migration (production workflow)
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

        # Write schema before generating so the client can be built
        prisma_dir = os.path.join(project_path, 'prisma')
        os.makedirs(prisma_dir, exist_ok=True)
        with open(os.path.join(prisma_dir, 'schema.prisma'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_PRISMA_SCHEMA)

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
        # Write src/db.js
        with open(os.path.join(project_path, 'src', 'db.js'), 'w', encoding='utf-8') as f:
            f.write(EXPRESS_PRISMA_DB_JS)

        # Inject import into app.js via battery marker
        app_js = os.path.join(project_path, 'src', 'app.ts')
        if not os.path.exists(app_js):
            app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{EXPRESS_PRISMA_IMPORT}// [BATTERY:IMPORTS]',
            )
            with open(app_js, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {app_js}[/bold red]')
            return

        # Add DATABASE_URL to .env.example
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
