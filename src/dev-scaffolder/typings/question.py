from typing import TypedDict, Literal, Optional, List


class TQuestion(TypedDict):
    """TypedDict for question structure - common fields

    Attributes:
        name (str): Unique identifier for the question.
        type (Literal): The UI element to use (list, text, multiselect, confirm, file).
        message (str): The actual prompt text shown to the user.
        choices (Optional[List[str]]): List of choices for 'list' or 'multiselect' types.
    """

    # Core fields
    name: str
    type: Literal['list', 'text', 'multiselect', 'confirm', 'file']
    message: str

    # List-specific fields
    choices: Optional[List[str]]


class TQuestionNonPopulated(TQuestion):
    """TypedDict for question structure

    Attributes:
        name (str): Unique identifier for the question.
        type (Literal): The UI element to use (list, text, multiselect, confirm, file).
        message (str): The actual prompt text shown to the user.
        choices (Optional[List[str]]): List of choices for 'list' or 'multiselect' types.
        children (List[str]): List of children file paths
    """
    # Children is a list of file paths
    children: List[str]


class TQuestionPopulated(TQuestion):
    """TypedDict for question structure with children attached

    Attributes:
        name (str): Unique identifier for the question.
        type (Literal): The UI element to use (list, text, multiselect, confirm, file).
        message (str): The actual prompt text shown to the user.
        choices (Optional[List[str]]): List of choices for 'list' or 'multiselect' types.
        children (List[TQuestionPopulated]): Populated children data.
    """
    # Children is a list of TQuestionPopulated
    children: List[TQuestionPopulated]