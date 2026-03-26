import os
import copy
from pathlib import Path
from typing import List, cast, Any, Optional

from typings.question import TQuestionPopulated, TQuestionNonPopulated
from utils.base import open_a_json_file

root_folder = Path(__file__).parent.parent

def get_question_children(questions: TQuestionNonPopulated) -> TQuestionPopulated:
    """
    Recursively populate question children by loading referenced files.

    Args:
        questions: TQuestionNonPopulated object with children as list of file paths

    Returns:
        TQuestionPopulated object with children as list of populated questions
    """
    children = questions.get("children", None)
    resolved_questions = cast(TQuestionPopulated, cast(Any, copy.deepcopy(questions)))
    resolved_questions["children"] = []

    if children is not None:
        non_populated_questions: List[str] = list(filter(lambda child: isinstance(child, str), children))
        if len(non_populated_questions) > 0:
            for question_path in non_populated_questions:
                # split to avoid forward slash issues on some os
                question_path_splits = question_path.split("/")
                full_question_path = os.path.join(
                    root_folder,
                    'questions',
                    *question_path_splits
                )
                question_resolved_data: Optional[TQuestionNonPopulated] = open_a_json_file(full_question_path)
                if question_resolved_data is not None:
                    inner_child = question_resolved_data.get("children", None)
                    inner_child_populated = []
                    if inner_child is not None:
                        inner_child_populated = get_question_children(question_resolved_data)
                    resolved_questions.get("children").append(inner_child_populated)
        else:
            resolved_questions["children"] = cast(List[TQuestionPopulated], cast(Any, children))

    return resolved_questions



def load_questions() -> Optional[TQuestionPopulated]:
    """
    Resolves and populates questions from a JSON file.

    This function reads a JSON file containing question data, processes the data to resolve
    any nested structures, and returns the populated question structure. If the file is not
    found or contains invalid JSON, appropriate warnings are logged.

    :return: The resolved and populated questions, or None if an error occurs.
    :rtype: Optional[TQuestionPopulated]
    """
    questions_path = os.path.join(root_folder, 'questions', 'base.json')

    question_data: Optional[TQuestionNonPopulated] = open_a_json_file(questions_path)
    if question_data is None:
        return None

    questions_resolved = get_question_children(question_data)
    return questions_resolved