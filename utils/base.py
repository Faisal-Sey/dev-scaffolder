import json
import os.path
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

from typings.base import SubProcessReturnCodeEnum, WriteToFileContent, ExecutorResponseStatus

root_folder = Path(__file__).parent.parent


def clean_name(name: str) -> str:
    """
    This function cleans the name question JSON, to match with the answer selected

    :param name: Name to clean
    :return: String of cleaned name, eg: Mobile App -> mobile_app
    """

    return (name.lower()
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "_")
            .replace("/", "_"))


def build_answers_path(
        previous_answer_path: str,
        current_answer: str
) -> str:
    """
    This function builds answer paths

    :param previous_answer_path: Already constructed choices selected
    :param current_answer: Current selected choice
    :return: Returns a constructed answer path
    """
    return previous_answer_path + "/" + clean_name(current_answer).title()


def open_a_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Opens and parses a JSON file into a Python dictionary. If the file does not exist or if the file
    contains invalid JSON, returns None and logs a warning message.

    :param file_path: The path to the JSON file to be opened.
    :type file_path: str
    :return: A dictionary containing the contents of the JSON file if successful, or None if the
             file does not exist or contains invalid JSON data.
    :rtype: Optional[Dict[str, Any]]
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Warning: Questions file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {file_path}: {e}")
        return None


def run_python_file(file_path: str, inputs: Dict[str, str]) -> None:
    """
    Execute a Python script with provided command-line arguments.

    This function allows you to run a Python script, specified by its file path,
    with additional command-line arguments represented as key-value pairs. Each
    key-value pair in the `inputs` dictionary will be passed to the script as
    command-line arguments in the format `--key value`.

    :param file_path: The path to the Python script that will be executed.
    :type file_path: str
    :param inputs: A dictionary where each key-value pair represents a
                   command-line argument to pass to the script. Each key
                   will be prefixed with '--' in the arguments list.
    :type inputs: Dict[str, str]
    :return: This function does not return any value.
    :rtype: None
    """
    args = [sys.executable, file_path]

    if inputs is not None:
        for key, value in inputs.items():
            args.append(f"--{key}")
            args.append(value)

    subprocess.run(args)


def check_or_create_venv() -> None:
    """
    Checks if a Python virtual environment (venv) exists in the specified directory and
    creates a new one if it does not already exist.

    This function ensures that a virtual environment is set up in the 'venv' subdirectory
    within the root folder. If the directory does not exist, it creates the environment
    using the `venv` module and the current Python interpreter.

    :param None: This function does not accept any parameters.
    :return: None
    """
    full_venv_path = os.path.join(root_folder, 'venv')
    if not os.path.exists(full_venv_path):
        subprocess.run([sys.executable, '-m venv venv'])


def get_venv_python_executor() -> str:
    """
    Retrieves the path to the Python executor within a virtual environment. The function determines
    the appropriate path based on the current operating system, considering differences in file
    structure between Windows and other platforms.

    :return: The absolute path to the virtual environment's Python executor.
    :rtype: str
    """
    full_venv_path = os.path.join(root_folder, 'venv')
    if sys.platform == "win32":
        python_path = os.path.join(full_venv_path, "Scripts", "python.exe")
    else:
        python_path = os.path.join(full_venv_path, "bin", "python")

    return python_path


def run_subprocess_command(script: List[str]) -> bool:
    try:
        command_result = subprocess.run(
            script,
            capture_output=True,
            text=True
        )

        if command_result.returncode != SubProcessReturnCodeEnum.SUCCESS.value:
            return False

        return True
    except Exception as e:
        print(f"Error running subprocess: {e}")
        return False


def activate_venv() -> None:
    is_activated = False

    # Windows-specific environment
    scripts_path = os.path.join(root_folder, 'venv', 'Scripts')

    if os.path.exists(scripts_path):
        # run bat
        ps1_script = os.path.join(scripts_path, 'Activate.ps1')
        bat_script = os.path.join(scripts_path, 'activate.bat')
        activate_script = os.path.join(scripts_path, 'activate')

        print("script", ps1_script)

        if os.path.exists(ps1_script):
            is_activated = run_subprocess_command([
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-File', ps1_script
            ])
        elif os.path.exists(bat_script) and (not is_activated):
            is_activated = run_subprocess_command(['source', bat_script])
        else:
            is_activated = run_subprocess_command(['source', activate_script])

    else:
        # Unix-specific environment
        bin_path = os.path.join(root_folder, 'venv', 'bin')

        fish_file = os.path.join(bin_path, 'activate.fish')
        csh_file = os.path.join(bin_path, 'activate.csh')
        activate_file = os.path.join(bin_path, 'activate')

        if os.path.exists(fish_file):
            is_activated = run_subprocess_command(['source', fish_file])

        elif os.path.exists(csh_file) and (not is_activated):
            is_activated = run_subprocess_command(['source', csh_file])
        else:
            is_activated = run_subprocess_command(['source', activate_file])


    if is_activated:
        print("Virtual environment activated successfully")
    else:
        print("Failed to activate virtual environment")

    return None


def write_into_file(path: str, contents: List[WriteToFileContent]) -> ExecutorResponseStatus:
    lines = []
    is_modified = False

    try:
        with open(path, "r") as f:
            lines = f.readlines()

    except FileNotFoundError:
        print(f"Failed to write into {path}")
        return ExecutorResponseStatus(success=False)

    if len(contents) > 0:
        for content in contents:
            if len(lines) == 0:
                lines.append(content.content)
            else:
                lines[content.line] = content.content
            is_modified = True

    try:
        if is_modified:
            with open(path, "w") as f:
                f.writelines(lines)

        return ExecutorResponseStatus(success=True)

    except FileNotFoundError:
        print(f"Failed to write into {path}")
        return ExecutorResponseStatus(success=False)
