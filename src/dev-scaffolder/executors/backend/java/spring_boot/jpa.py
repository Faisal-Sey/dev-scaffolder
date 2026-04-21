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
from constants.backend.java.spring_boot.base import (
    SPRING_BOOT_JPA_POM_XML,
    SPRING_BOOT_APPLICATION_JAVA,
    SPRING_BOOT_HEALTH_CONTROLLER_JAVA,
    SPRING_BOOT_APPLICATION_TEST_JAVA,
    SPRING_BOOT_GITIGNORE,
    SPRING_BOOT_JPA_APPLICATION_PROPERTIES,
    SPRING_BOOT_ENV,
    SPRING_BOOT_ENV_EXAMPLE,
    SPRING_BOOT_USER_ENTITY_JAVA,
    SPRING_BOOT_USER_REPOSITORY_JAVA,
    SPRING_BOOT_USER_SERVICE_JPA_JAVA,
    SPRING_BOOT_USER_CONTROLLER_JPA_JAVA,
)


def _pkg(project_name: str) -> str:
    return re.sub(r'[^a-z0-9]', '', project_name.lower()) or 'app'


class SpringBootJpaExecutor(BaseExecutor):
    """Scaffolds a Spring Boot 3 project with JPA and H2 in-memory database."""

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

        write(os.path.join(main_java, 'Application.java'), SPRING_BOOT_APPLICATION_JAVA)
        write(os.path.join(main_java, 'HealthController.java'), SPRING_BOOT_HEALTH_CONTROLLER_JAVA)
        write(os.path.join(users_java, 'User.java'), SPRING_BOOT_USER_ENTITY_JAVA)
        write(os.path.join(users_java, 'UserRepository.java'), SPRING_BOOT_USER_REPOSITORY_JAVA)
        write(os.path.join(users_java, 'UserService.java'), SPRING_BOOT_USER_SERVICE_JPA_JAVA)
        write(os.path.join(users_java, 'UserController.java'), SPRING_BOOT_USER_CONTROLLER_JPA_JAVA)
        write(os.path.join(main_res, 'application.properties'), SPRING_BOOT_JPA_APPLICATION_PROPERTIES)
        write(os.path.join(test_java, 'ApplicationTests.java'), SPRING_BOOT_APPLICATION_TEST_JAVA)
        write(os.path.join(project_path, 'pom.xml'), SPRING_BOOT_JPA_POM_XML)
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

        self._write_readme(project_path, project_name=project_name)
        self.console.print(
            f"[bold green]Spring Boot JPA project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Spring Boot 3 project with JPA and H2 in-memory database scaffolded by dev-scaffolder.\n\n'
            '## Endpoints\n\n'
            '| Method | Path | Description |\n'
            '|--------|------|-------------|\n'
            '| GET | /api/users | List all users |\n'
            '| GET | /api/users/{id} | Get user by ID |\n'
            '| POST | /api/users | Create user |\n'
            '| PUT | /api/users/{id} | Update user |\n'
            '| DELETE | /api/users/{id} | Delete user |\n\n'
            '## H2 Console\n\n'
            'Available at http://localhost:8080/h2-console\n\n'
            '## Run\n\n'
            '```bash\n'
            'mvn spring-boot:run\n'
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


def generate_spring_boot_jpa_template(**kwargs) -> ExecutorResponseStatus:
    return SpringBootJpaExecutor().run(**kwargs)


if __name__ == '__main__':
    args = SpringBootJpaExecutor.build_arg_parser().parse_args()
    SpringBootJpaExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
    )