import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import NESTJS_CORS_SETUP
from typings.base import ExecutorResponseStatus


class NestJSCORSBattery(BaseBattery):
    """
    Battery that enables CORS on a NestJS app.

    Calls app.enableCors() in main.ts — no extra packages required as
    CORS support is built into @nestjs/core.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        main_ts = os.path.join(project_path, 'src', 'main.ts')
        try:
            with open(main_ts, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '  // [BATTERY:SETUP]',
                f'{NESTJS_CORS_SETUP}  // [BATTERY:SETUP]',
            )
            with open(main_ts, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {main_ts}[/bold red]')