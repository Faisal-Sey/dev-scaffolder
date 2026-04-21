import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.nestjs.base import (
    NESTJS_MONGOOSE_IMPORT,
    NESTJS_MONGOOSE_MODULE_IMPORT,
)
from typings.base import ExecutorResponseStatus


class NestJSMongooseBattery(BaseBattery):
    """
    Battery that adds Mongoose (MongoDB ODM) to a NestJS app.

    Installs '@nestjs/mongoose' and 'mongoose', then injects
    MongooseModule.forRoot() into app.module.ts imports.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        npm = shutil.which('npm') or 'npm'
        result = subprocess.run(
            [npm, 'install', '@nestjs/mongoose', 'mongoose'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f'[bold red]Failed to install @nestjs/mongoose: {result.stderr}[/bold red]'
            )
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        module_import = NESTJS_MONGOOSE_MODULE_IMPORT.replace('{project_name}', project_name)

        app_module = os.path.join(project_path, 'src', 'app.module.ts')
        try:
            with open(app_module, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{NESTJS_MONGOOSE_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '    // [BATTERY:MODULE_IMPORTS]',
                f'{module_import}    // [BATTERY:MODULE_IMPORTS]',
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
            if 'MONGODB_URI' not in content:
                content += f'MONGODB_URI=mongodb://localhost:27017/{project_name}\n'
            with open(env_example, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            pass