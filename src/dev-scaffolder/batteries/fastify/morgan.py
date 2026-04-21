import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus

FASTIFY_PINO_PRETTY_INDEX_JS = """\
'use strict';

require('dotenv').config();
const app = require('./app');

const PORT = process.env.PORT || 3000;

const start = async () => {
  try {
    await app.listen({ port: PORT, host: '0.0.0.0' });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
"""

FASTIFY_PINO_PRETTY_APP_JS_HEADER = """\
'use strict';

const fastify = require('fastify')({
  logger: {
    transport: process.env.NODE_ENV !== 'production'
      ? { target: 'pino-pretty', options: { colorize: true } }
      : undefined,
  },
});

"""


class FastifyMorganBattery(BaseBattery):
    """
    Battery that adds pretty request logging to a Fastify app via pino-pretty.

    Installs 'pino-pretty' and configures Fastify's built-in pino logger to
    use colourised output in non-production environments. This is the Fastify
    equivalent of Morgan's dev-mode logging for Express.
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        npm = shutil.which('npm') or 'npm'
        result = subprocess.run(
            [npm, 'install', '--save-dev', 'pino-pretty'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f'[bold red]Failed to install pino-pretty: {result.stderr}[/bold red]'
            )
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace the plain fastify({ logger: true }) initialiser with the
            # pino-pretty-aware version if the default pattern is present.
            old_init = "const fastify = require('fastify')({ logger: true });"
            if old_init in content:
                new_init = (
                    "const fastify = require('fastify')({\n"
                    "  logger: {\n"
                    "    transport: process.env.NODE_ENV !== 'production'\n"
                    "      ? { target: 'pino-pretty', options: { colorize: true } }\n"
                    "      : undefined,\n"
                    "  },\n"
                    "});"
                )
                content = content.replace(old_init, new_init)
                with open(app_js, 'w', encoding='utf-8') as f:
                    f.write(content)
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {app_js}[/bold red]')