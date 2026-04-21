import argparse
import os
import re
import shutil
import subprocess
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from batteries.base import BaseBattery
from typings.base import ExecutorResponseStatus
from constants.backend.java.spring_boot.base import (
    SPRING_BOOT_POM_XML,
    SPRING_BOOT_APPLICATION_JAVA,
    SPRING_BOOT_HEALTH_CONTROLLER_JAVA,
    SPRING_BOOT_APPLICATION_PROPERTIES,
    SPRING_BOOT_APPLICATION_TEST_JAVA,
    SPRING_BOOT_GITIGNORE,
    SPRING_BOOT_ENV,
    SPRING_BOOT_ENV_EXAMPLE,
)


def _pkg(project_name: str) -> str:
    return re.sub(r'[^a-z0-9]', '', project_name.lower()) or 'app'


class SpringBootOfficialExecutor(BaseExecutor):
    """Scaffolds a base Spring Boot 3 project with Maven."""

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        mvn = shutil.which('mvn')
        if not mvn:
            raise RuntimeError('mvn not found in PATH. Please install Maven.')
        return mvn

    def install_dependencies(self, mvn_path: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def _resolve_dependencies(self, project_path: str) -> ExecutorResponseStatus:
        self._update_status('[bold blue]Resolving Maven dependencies...[/bold blue]')
        mvn = self.get_venv_environment()
        result = subprocess.run(
            [mvn, 'dependency:resolve', '-q'],
            cwd=project_path, capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.console.print(f'[bold red]mvn dependency:resolve failed:[/bold red]\n{result.stderr}')
            return ExecutorResponseStatus(success=False)
        return ExecutorResponseStatus(success=True)

    def _create_project_structure(self, project_path: str, project_name: str) -> None:
        pkg = _pkg(project_name)
        pkg_path = os.path.join(*(['com', 'example'] + [pkg]))

        main_java = os.path.join(project_path, 'src', 'main', 'java', 'com', 'example', pkg)
        main_res = os.path.join(project_path, 'src', 'main', 'resources')
        test_java = os.path.join(project_path, 'src', 'test', 'java', 'com', 'example', pkg)

        for d in [main_java, main_res, test_java]:
            os.makedirs(d, exist_ok=True)

        def write(path, content):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.replace('{project_name}', project_name).replace('{package_name}', pkg))

        write(os.path.join(main_java, 'Application.java'), SPRING_BOOT_APPLICATION_JAVA)
        write(os.path.join(main_java, 'HealthController.java'), SPRING_BOOT_HEALTH_CONTROLLER_JAVA)
        write(os.path.join(main_res, 'application.properties'), SPRING_BOOT_APPLICATION_PROPERTIES)
        write(os.path.join(test_java, 'ApplicationTests.java'), SPRING_BOOT_APPLICATION_TEST_JAVA)
        write(os.path.join(project_path, 'pom.xml'), SPRING_BOOT_POM_XML)
        write(os.path.join(project_path, '.gitignore'), SPRING_BOOT_GITIGNORE)
        write(os.path.join(project_path, '.env'), SPRING_BOOT_ENV)
        write(os.path.join(project_path, '.env.example'), SPRING_BOOT_ENV_EXAMPLE)

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

        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name)

        self.console.print(
            f"[bold green]Spring Boot project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Spring Boot 3 project scaffolded with dev-scaffolder.\n\n'
            '## Requirements\n\n'
            '- Java 21+\n'
            '- Maven 3.9+\n\n'
            '## Setup\n\n'
            '```bash\n'
            'cp .env.example .env\n'
            'mvn dependency:resolve\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'mvn spring-boot:run\n'
            '```\n\n'
            '## Build\n\n'
            '```bash\n'
            'mvn package -DskipTests\n'
            'java -jar target/*.jar\n'
            '```\n\n'
            '## Test\n\n'
            '```bash\n'
            'mvn test\n'
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


def generate_spring_boot_official_template(**kwargs) -> ExecutorResponseStatus:
    return SpringBootOfficialExecutor().run(**kwargs)


if __name__ == '__main__':
    args = SpringBootOfficialExecutor.build_arg_parser().parse_args()
    SpringBootOfficialExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
    )
