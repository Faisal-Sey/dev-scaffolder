import argparse
import os
import re
import shutil
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from typings.base import ExecutorResponseStatus
from constants.backend.java.quarkus.base import (
    QUARKUS_PANACHE_POM_XML,
    QUARKUS_GREETING_RESOURCE_JAVA,
    QUARKUS_PANACHE_APPLICATION_PROPERTIES,
    QUARKUS_GITIGNORE,
    QUARKUS_ENV,
    QUARKUS_ENV_EXAMPLE,
    QUARKUS_PANACHE_ENTITY_JAVA,
    QUARKUS_PANACHE_RESOURCE_JAVA,
)


def _pkg(project_name: str) -> str:
    return re.sub(r'[^a-z0-9]', '', project_name.lower()) or 'app'


class QuarkusHibernatePanacheExecutor(BaseExecutor):
    """Scaffolds a Quarkus 3 project with Hibernate ORM Panache and H2."""

    def get_venv_environment(self) -> str:
        mvn = shutil.which('mvn')
        if not mvn:
            raise RuntimeError('mvn not found in PATH. Please install Maven.')
        return mvn

    def install_dependencies(self, mvn_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def _resolve_dependencies(self, project_path: str) -> ExecutorResponseStatus:
        self._update_status('[bold blue]Resolving Maven dependencies...[/bold blue]')
        result = subprocess.run(
            [self.get_venv_environment(), 'dependency:resolve', '-q'],
            cwd=project_path, capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]mvn dependency:resolve failed:[/bold red]\n{result.stderr}')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        pkg = _pkg(project_name)

        main_java = os.path.join(project_path, 'src', 'main', 'java', 'com', 'example', pkg)
        users_java = os.path.join(main_java, 'users')
        main_res = os.path.join(project_path, 'src', 'main', 'resources')
        test_java = os.path.join(project_path, 'src', 'test', 'java', 'com', 'example', pkg)

        for d in [main_java, users_java, main_res, test_java]:
            os.makedirs(d, exist_ok=True)

        def write(path, content):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.replace('{project_name}', project_name).replace('{package_name}', pkg))

        write(os.path.join(main_java, 'GreetingResource.java'), QUARKUS_GREETING_RESOURCE_JAVA)
        write(os.path.join(users_java, 'User.java'), QUARKUS_PANACHE_ENTITY_JAVA)
        write(os.path.join(users_java, 'UserResource.java'), QUARKUS_PANACHE_RESOURCE_JAVA)
        write(os.path.join(main_res, 'application.properties'), QUARKUS_PANACHE_APPLICATION_PROPERTIES)
        write(os.path.join(project_path, 'pom.xml'), QUARKUS_PANACHE_POM_XML)
        write(os.path.join(project_path, '.gitignore'), QUARKUS_GITIGNORE)
        write(os.path.join(project_path, '.env'), QUARKUS_ENV)
        write(os.path.join(project_path, '.env.example'), QUARKUS_ENV_EXAMPLE)

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        project_path = os.path.join(self.current_folder, directory_name)

        if not self.prepare_directory(project_path).success:
            return ExecutorResponseStatus(success=False)

        self._update_status('[bold blue]Creating project structure...[/bold blue]')
        self._create_project_structure(project_path, project_name)

        if not self._resolve_dependencies(project_path).success:
            return ExecutorResponseStatus(success=False)

        self._write_readme(project_path, project_name=project_name)
        self.console.print(
            f"[bold green]Quarkus Hibernate Panache project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Quarkus 3 project with Hibernate ORM Panache and H2 scaffolded by dev-scaffolder.\n\n'
            '## Endpoints\n\n'
            '| Method | Path | Description |\n'
            '|--------|------|-------------|\n'
            '| GET | /api/users | List all users |\n'
            '| GET | /api/users/{id} | Get user by ID |\n'
            '| POST | /api/users | Create user |\n'
            '| PUT | /api/users/{id} | Update user |\n'
            '| DELETE | /api/users/{id} | Delete user |\n\n'
            '## Run (dev mode)\n\n'
            '```bash\n'
            'mvn quarkus:dev\n'
            '```\n\n'
            'Server runs at http://localhost:8080\n'
        )

    def generate(self, **kwargs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'myproject') or 'myproject'
        directory_name = kwargs.get('directory_name', '') or project_name
        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject')
        parser.add_argument('--directory_name', type=str, default='myproject')
        return parser


def generate_quarkus_hibernate_panache_template(**kwargs) -> ExecutorResponseStatus:
    return QuarkusHibernatePanacheExecutor().run(**kwargs)


if __name__ == '__main__':
    args = QuarkusHibernatePanacheExecutor.build_arg_parser().parse_args()
    QuarkusHibernatePanacheExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
    )