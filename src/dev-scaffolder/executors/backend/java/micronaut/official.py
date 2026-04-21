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
from constants.backend.java.micronaut.base import (
    MICRONAUT_POM_XML,
    MICRONAUT_APPLICATION_JAVA,
    MICRONAUT_HEALTH_CONTROLLER_JAVA,
    MICRONAUT_APPLICATION_YML,
    MICRONAUT_GITIGNORE,
    MICRONAUT_ENV,
    MICRONAUT_ENV_EXAMPLE,
)


def _pkg(project_name: str) -> str:
    return re.sub(r'[^a-z0-9]', '', project_name.lower()) or 'app'


class MicronautOfficialExecutor(BaseExecutor):
    """Scaffolds a base Micronaut 4 project with Maven."""

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
        main_res = os.path.join(project_path, 'src', 'main', 'resources')
        test_java = os.path.join(project_path, 'src', 'test', 'java', 'com', 'example', pkg)

        for d in [main_java, main_res, test_java]:
            os.makedirs(d, exist_ok=True)

        def write(path, content):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.replace('{project_name}', project_name).replace('{package_name}', pkg))

        write(os.path.join(main_java, 'Application.java'), MICRONAUT_APPLICATION_JAVA)
        write(os.path.join(main_java, 'HealthController.java'), MICRONAUT_HEALTH_CONTROLLER_JAVA)
        write(os.path.join(main_res, 'application.yml'), MICRONAUT_APPLICATION_YML)
        write(os.path.join(project_path, 'pom.xml'), MICRONAUT_POM_XML)
        write(os.path.join(project_path, '.gitignore'), MICRONAUT_GITIGNORE)
        write(os.path.join(project_path, '.env'), MICRONAUT_ENV)
        write(os.path.join(project_path, '.env.example'), MICRONAUT_ENV_EXAMPLE)

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
            f"[bold green]Micronaut project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Micronaut 4 project scaffolded with dev-scaffolder.\n\n'
            '## Requirements\n\n'
            '- Java 21+\n'
            '- Maven 3.9+\n\n'
            '## Run\n\n'
            '```bash\n'
            'mvn mn:run\n'
            '```\n\n'
            '## Build\n\n'
            '```bash\n'
            'mvn package -DskipTests\n'
            'java -jar target/*.jar\n'
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


def generate_micronaut_official_template(**kwargs) -> ExecutorResponseStatus:
    return MicronautOfficialExecutor().run(**kwargs)


if __name__ == '__main__':
    args = MicronautOfficialExecutor.build_arg_parser().parse_args()
    MicronautOfficialExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
    )