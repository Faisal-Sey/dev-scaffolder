import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from batteries.base import BaseBattery
from constants.backend.python.base import DJANGO_FACTORY_BOY_EXAMPLE
from typings.base import ExecutorResponseStatus
from utils.base import run_subprocess_command


class FactoryBoyBattery(BaseBattery):
    """
    Battery that installs factory_boy and writes a sample factory.

    Installs factory_boy, then creates:
      tests/factories.py  — UserFactory using get_user_model()
    """

    def install(self, venv_python_executor: str) -> ExecutorResponseStatus:
        command = [venv_python_executor, '-m', 'pip', 'install', 'factory_boy']
        if not run_subprocess_command(command):
            self.console.print("[bold red]Failed to install factory_boy[/bold red]")
            return ExecutorResponseStatus(success=False)
        self.console.print("[bold green]factory_boy installed successfully[/bold green]")
        return ExecutorResponseStatus(success=True)

    def configure(self, project_path: str, project_name: str, app_name: str) -> None:
        tests_dir = os.path.join(project_path, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        init_path = os.path.join(tests_dir, '__init__.py')
        if not os.path.exists(init_path):
            open(init_path, 'w').close()
        with open(os.path.join(tests_dir, 'factories.py'), 'w') as f:
            f.write(DJANGO_FACTORY_BOY_EXAMPLE)
        self.console.print("[bold green]factory_boy factories written[/bold green]")
