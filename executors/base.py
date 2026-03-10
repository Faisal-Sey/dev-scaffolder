import os
import shutil
import sys
import argparse
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

import inquirer
from rich.console import Console
from rich.status import Status

from typings.base import ExecutorResponseStatus
from utils.env import get_output_directory


class BaseExecutor(ABC):
    """
    Abstract base class defining the skeleton for all project scaffold executors.

    Subclasses must implement the core lifecycle methods. The public entry point
    is run(), which wraps generate() with a loading status spinner and provides
    helpers to pause/resume the spinner around interactive prompts.

    Standard execution flow:
        run() → [spinner starts] → generate() → prepare_directory()
                                               → execute_creation_commands()
                                                   → get_venv_environment()
                                                   → install_dependencies()
    """

    def __init__(self):
        self.current_folder = get_output_directory()
        self.console = Console()
        self._status: Optional[Status] = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, **kwargs):
        """
        Start a loading spinner, execute the template via generate(), then
        stop the spinner.

        This is the method to call from __main__ and external callers.

        :param kwargs: Forwarded verbatim to generate().
        :return: Whatever generate() returns.
        """
        with self.console.status(
            "[bold blue]Executing template...", spinner="bouncingBar"
        ) as status:
            self._status = status
            result = self.generate(**kwargs)
        self._status = None
        return result

    # ------------------------------------------------------------------
    # Status helpers (for subclasses to use around interactive prompts)
    # ------------------------------------------------------------------

    def _stop_status(self) -> None:
        """Pause the spinner before an interactive prompt."""
        if self._status is not None:
            self._status.stop()

    def _start_status(self) -> None:
        """Resume the spinner after an interactive prompt."""
        if self._status is not None:
            self._status.start()

    def _update_status(self, message: str) -> None:
        """Update the spinner message to reflect the current step."""
        if self._status is not None:
            self._status.update(message)

    # ------------------------------------------------------------------
    # Abstract lifecycle methods
    # ------------------------------------------------------------------

    @abstractmethod
    def get_venv_environment(self) -> str:
        """
        Retrieve the Python executable path for the virtual environment.

        Should ensure a venv exists, activate it, and return the path to
        the Python interpreter inside it.

        :return: Path to the venv Python executable.
        :rtype: str
        """
        ...

    @abstractmethod
    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        """
        Install the required packages for this executor's framework.

        :param venv_python_executor: Path to the venv Python executable.
        :type venv_python_executor: str
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        ...

    def prepare_directory(self, directory_full_path: str) -> ExecutorResponseStatus:
        """
        Ensure the target directory is ready for scaffolding.

        Creates the directory if it does not exist. If it already exists,
        pauses the spinner and prompts the user to confirm replacement.
        Refuses to delete the current working directory.

        Override in a subclass only if the executor needs different behaviour.

        :param directory_full_path: Absolute path to the target directory.
        :type directory_full_path: str
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        if os.path.abspath(directory_full_path) == os.path.abspath(self.current_folder):
            self.console.print("[bold red]Cannot delete the root directory[/bold red]")
            return ExecutorResponseStatus(success=False)

        if os.path.exists(directory_full_path):
            prompt = [
                inquirer.Confirm(
                    "replace_directory",
                    message="Directory exists, do you want to replace the content",
                    default=True
                )
            ]

            self._stop_status()
            answers = inquirer.prompt(prompt)
            self._start_status()

            if answers is None:
                self.console.print("[bold yellow]You selected a wrong option or cancelled[/bold yellow]")
                return ExecutorResponseStatus(success=False)

            if answers.get("replace_directory"):
                shutil.rmtree(directory_full_path)
                os.makedirs(directory_full_path)
            else:
                return ExecutorResponseStatus(success=False)
        else:
            os.makedirs(directory_full_path)

        return ExecutorResponseStatus(success=True)

    @abstractmethod
    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Orchestrate all commands needed to scaffold the project.

        This typically involves calling get_venv_environment,
        install_dependencies, and any framework-specific creation steps.
        Use self._update_status(message) to reflect the current step in the
        spinner rather than creating nested console.status() contexts.

        :param kwargs: Framework-specific arguments (e.g. project_name, app_name).
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        ...

    @abstractmethod
    def generate(self, **kwargs):
        """
        Internal implementation for generating the project template.

        Should resolve arguments, call prepare_directory, and then invoke
        execute_creation_commands. Called by run(); do not call directly.

        :param kwargs: Arbitrary keyword arguments for project configuration.
        """
        ...

    # ------------------------------------------------------------------
    # CLI helpers
    # ------------------------------------------------------------------

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        """
        Build an ArgumentParser for running this executor as a CLI script.

        Override in subclasses to add framework-specific arguments.

        :return: Configured ArgumentParser instance.
        :rtype: argparse.ArgumentParser
        """
        return argparse.ArgumentParser(
            description=f"Generate project template using {cls.__name__}"
        )