import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.express.base import (
    EXPRESS_HELMET_IMPORT,
    EXPRESS_HELMET_MIDDLEWARE,
)
from typings.base import ExecutorResponseStatus


class ExpressHelmetBattery(BaseBattery):
    """
    Battery that adds the helmet security middleware to an Express app.

    Installs 'helmet' and inserts the import and app.use(helmet()) call
    into src/app.js via battery markers.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        result = subprocess.run(
            [shutil.which('npm') or 'npm', 'install', 'helmet'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]Failed to install helmet: {result.stderr}[/bold red]')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{EXPRESS_HELMET_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '// [BATTERY:MIDDLEWARE]',
                f'{EXPRESS_HELMET_MIDDLEWARE}// [BATTERY:MIDDLEWARE]',
            )
            with open(app_js, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {app_js}[/bold red]')
