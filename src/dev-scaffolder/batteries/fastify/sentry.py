import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus

FASTIFY_SENTRY_IMPORT = "const Sentry = require('@sentry/node');\n"

FASTIFY_SENTRY_SETUP = """\
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV || 'development',
});
"""


class FastifySentryBattery(BaseBattery):
    """
    Battery that adds Sentry error tracking to a Fastify app.

    Installs '@sentry/node' and initialises Sentry with the DSN from
    SENTRY_DSN env var at startup, before route registration.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        npm = shutil.which('npm') or 'npm'
        result = subprocess.run(
            [npm, 'install', '@sentry/node'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f'[bold red]Failed to install @sentry/node: {result.stderr}[/bold red]'
            )
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{FASTIFY_SENTRY_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '// [BATTERY:PLUGINS]',
                f'{FASTIFY_SENTRY_SETUP}// [BATTERY:PLUGINS]',
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
            if 'SENTRY_DSN' not in content:
                content += 'SENTRY_DSN=\n'
            with open(env_example, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            pass