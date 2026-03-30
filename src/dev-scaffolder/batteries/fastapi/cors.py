import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.fastapi.base import (
    FASTAPI_CORS_MIDDLEWARE_CODE,
    FASTAPI_CORS_MIDDLEWARE_SETUP,
)
from typings.base import ExecutorResponseStatus


class FastAPICORSBattery(BaseBattery):
    """
    Battery that adds CORSMiddleware to the FastAPI app.

    No packages are installed (CORSMiddleware ships with fastapi).
    Inserts the import and app.add_middleware() call into main.py
    using the [BATTERY:IMPORTS] and [BATTERY:MIDDLEWARE] markers.
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        main_py = os.path.join(project_path, 'app', 'main.py')
        try:
            with open(main_py, 'r') as f:
                content = f.read()
            content = content.replace(
                '# [BATTERY:IMPORTS]',
                f'{FASTAPI_CORS_MIDDLEWARE_CODE}# [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '# [BATTERY:MIDDLEWARE]',
                f'{FASTAPI_CORS_MIDDLEWARE_SETUP}# [BATTERY:MIDDLEWARE]',
            )
            with open(main_py, 'w') as f:
                f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {main_py}[/bold red]')
