import os
from pathlib import Path

from dotenv import load_dotenv

root_folder = Path(__file__).parent.parent

# Load .env from the project root
load_dotenv(dotenv_path=root_folder / ".env")

_DEVELOPMENT = "development"


def get_environment() -> str:
    """
    Return the value of the ENVIRONMENT variable from .env.

    :return: Environment string, e.g. "development" or "production".
    :rtype: str
    """
    return os.getenv("ENVIRONMENT", "production").lower()


def is_development() -> bool:
    """
    Return True when ENVIRONMENT is set to "development".

    :return: True if running in development mode.
    :rtype: bool
    """
    return get_environment() == _DEVELOPMENT


def get_output_directory() -> str:
    """
    Return the directory where generated projects should be created.

    In development, this is <project_root>/temp so it can be excluded
    from version control. In all other environments it is the current
    working directory.

    :return: Absolute path to the output directory.
    :rtype: str
    """
    if is_development():
        output_dir = root_folder / "temp"
        output_dir.mkdir(exist_ok=True)
        return str(output_dir)
    return os.getcwd()


def get_venv_directory() -> str:
    """
    Return the directory where the virtual environment should be created.

    In development, this is <project_root>/temp/venv so it can be excluded
    from version control alongside generated projects. In all other
    environments it is <project_root>/venv.

    :return: Absolute path to the venv directory.
    :rtype: str
    """
    if is_development():
        return str(root_folder / "temp" / "venv")
    return str(root_folder / "venv")