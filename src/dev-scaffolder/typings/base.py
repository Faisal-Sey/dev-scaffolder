from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class SubProcessReturnCodeEnum(Enum):
    SUCCESS = 0
    FAILED = 1


@dataclass
class WriteToFileContent:
    # starts at 0
    line: int
    content: str


class DjangoOfficialTemplateArgs(TypedDict):
    """
    Represents a typed dictionary for Django official template arguments.

    This class is used to define a structure for the arguments required to set up
    a Django project using the official template. It ensures that the provided
    data adheres to the specified keys and value types, which are typically used to
    initialize a Django project directory and structure.

    :ivar project_name: The name of the Django project.
    :type project_name: str
    :ivar directory_name: The name of the directory where the project will be created.
    :type directory_name: str
    """
    project_name: str
    directory_name: str


@dataclass
class ExecutorResponseStatus:
    success: bool
    message: str = ""


@dataclass
class DjangoOfficialTemplateResponse:
    success: bool
    message: str = ""
    path: str = ""