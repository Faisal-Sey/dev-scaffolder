import json
import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.javascript.fastify.base import FASTIFY_EXAMPLE_TEST_JS
from typings.base import ExecutorResponseStatus


class FastifyJestBattery(BaseBattery):
    """
    Battery that adds Jest testing to a Fastify app.

    Installs 'jest', adds a "test" script to package.json, configures the
    jest testEnvironment, and writes an example test that uses fastify.inject().
    """

    def install(self, project_path: str) -> ExecutorResponseStatus:
        result = subprocess.run(
            [shutil.which('npm') or 'npm', 'install', '--save-dev', 'jest'],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]Failed to install jest: {result.stderr}[/bold red]')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        pkg_path = os.path.join(project_path, 'package.json')
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
            pkg.setdefault('scripts', {})['test'] = 'jest'
            pkg['jest'] = {'testEnvironment': 'node'}
            with open(pkg_path, 'w', encoding='utf-8') as f:
                json.dump(pkg, f, indent=2)
                f.write('\n')
        except FileNotFoundError:
            self.console.print(f'[bold red]File not found: {pkg_path}[/bold red]')
            return

        tests_dir = os.path.join(project_path, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        with open(os.path.join(tests_dir, 'app.test.js'), 'w', encoding='utf-8') as f:
            f.write(FASTIFY_EXAMPLE_TEST_JS)
