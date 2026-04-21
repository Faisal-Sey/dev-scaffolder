import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus

FASTIFY_SEQUELIZE_DB_JS = """\
'use strict';

const { Sequelize } = require('sequelize');

const sequelize = new Sequelize({
  dialect: process.env.DB_DIALECT || 'sqlite',
  storage: process.env.DATABASE_URL || './data.sqlite',
  logging: process.env.NODE_ENV !== 'production',
});

module.exports = { sequelize };
"""

FASTIFY_SEQUELIZE_IMPORT = "const { sequelize } = require('./db');\n"

FASTIFY_SEQUELIZE_SETUP = """\
sequelize.authenticate()
  .then(() => fastify.log.info('Database connected'))
  .catch((err) => { fastify.log.error(err); process.exit(1); });
"""


class FastifySequelizeBattery(BaseBattery):
    """
    Battery that adds Sequelize ORM to a Fastify app.

    Installs 'sequelize' and 'sqlite3' (zero-config default dialect),
    creates src/db.js with the Sequelize instance, injects the import and
    authenticate() call into src/app.js, and adds DATABASE_URL to .env.example.

    To switch dialect, set DB_DIALECT and DATABASE_URL in .env and install
    the matching driver (pg, mysql2, tedious, etc.).
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        npm = shutil.which('npm') or 'npm'
        result = subprocess.run(
            [npm, 'install', 'sequelize', 'sqlite3'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f'[bold red]Failed to install sequelize: {result.stderr}[/bold red]'
            )
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        with open(os.path.join(project_path, 'src', 'db.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_SEQUELIZE_DB_JS)

        app_js = os.path.join(project_path, 'src', 'app.js')
        try:
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                '// [BATTERY:IMPORTS]',
                f'{FASTIFY_SEQUELIZE_IMPORT}// [BATTERY:IMPORTS]',
            )
            content = content.replace(
                '// [BATTERY:PLUGINS]',
                f'{FASTIFY_SEQUELIZE_SETUP}// [BATTERY:PLUGINS]',
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
            if 'DATABASE_URL' not in content:
                content += 'DATABASE_URL=./data.sqlite\nDB_DIALECT=sqlite\n'
            with open(env_example, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            pass