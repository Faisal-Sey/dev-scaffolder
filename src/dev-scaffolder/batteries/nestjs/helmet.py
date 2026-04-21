import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import (
    NESTJS_HELMET_IMPORT,
    NESTJS_HELMET_SETUP,
)
from typings.base import ExecutorResponseStatus


class NestJSHelmetBattery(BaseBattery):
    """
    Battery that adds Helmet security headers to a NestJS app.

    Installs 'helmet' and applies it as Express middleware via app.use(helmet())
    in main.ts. Works with the default @nestjs/platform-express adapter.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        npm = shutil.which('npm') or 'npm'
        result = subprocess.run(
            [npm, 'install', 'helmet'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f'[bold red]Failed to install helmet: {result.stderr}[/bold red]'
            )
            return ExecutorResponseStatus(success=False)

        result = subprocess.run(
            [npm, 'install', '--save-dev', '@types/helmet'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        main_ts = os.path.join(project_path, 'src', 'main.ts')
        try:
            with open(main_ts, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{NESTJS_HELMET_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '  // [BATTERY:SETUP]',
                f'{NESTJS_HELMET_SETUP}  // [BATTERY:SETUP]',
            )
            with open(main_ts, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {main_ts}[/bold red]')