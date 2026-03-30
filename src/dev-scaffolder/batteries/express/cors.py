import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.express.base import (
    EXPRESS_CORS_IMPORT,
    EXPRESS_CORS_MIDDLEWARE,
)
from typings.base import ExecutorResponseStatus


class ExpressCORSBattery(BaseBattery):
    """
    Battery that adds the cors middleware to an Express app.

    Installs the 'cors' npm package and inserts the import and
    app.use(cors()) call into src/app.js via battery markers.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        result = subprocess.run(
            [shutil.which('npm') or 'npm', 'install', 'cors'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]Failed to install cors: {result.stderr}[/bold red]')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_js = os.path.join(project_path, 'src', 'app.ts')
        if not os.path.exists(app_js):
            app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{EXPRESS_CORS_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '// [BATTERY:MIDDLEWARE]',
                f'{EXPRESS_CORS_MIDDLEWARE}// [BATTERY:MIDDLEWARE]',
            )
            with open(app_js, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {app_js}[/bold red]')
