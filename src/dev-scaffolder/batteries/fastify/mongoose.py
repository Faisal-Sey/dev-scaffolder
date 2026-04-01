import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.fastify.base import (
    FASTIFY_MONGOOSE_IMPORT,
    FASTIFY_MONGOOSE_SETUP,
)
from typings.base import ExecutorResponseStatus


class FastifyMongooseBattery(BaseBattery):
    """
    Battery that adds Mongoose (MongoDB ODM) to a Fastify app.

    Installs 'mongoose', injects the import into src/app.js, and adds
    the mongoose.connect() call so the database connects on startup.
    Also adds MONGODB_URI to .env.example.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        result = subprocess.run(
            [shutil.which('npm') or 'npm', 'install', 'mongoose'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]Failed to install mongoose: {result.stderr}[/bold red]')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
            setup = FASTIFY_MONGOOSE_SETUP.replace('{project_name}', project_name)
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{FASTIFY_MONGOOSE_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '// [BATTERY:PLUGINS]',
                f'{setup}// [BATTERY:PLUGINS]',
            )
            with open(app_js, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {app_js}[/bold red]')
            return

        env_example = os.path.join(project_path, '.env.example')
        try:
            with open(env_example, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'MONGODB_URI' not in content:
                content += f'MONGODB_URI=mongodb://localhost:27017/{project_name}\n'
            with open(env_example, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            pass
