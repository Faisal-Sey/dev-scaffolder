import os
from pathlib import Path
from typing import Optional, List, Dict

import inquirer

from processors.get_inquirer import get_inquirer_instance
from typings.question import TQuestionNonPopulated, TQuestionPopulated
from utils.base import open_a_json_file, run_python_file

root_folder = Path(__file__).parent.parent

def get_question_json(answer_path: str) -> Optional[TQuestionNonPopulated]:
    """
    This retrieves the question content based on provided answer_path

    :param answer_path: The already built answer path
    :return: Returns question content
    """
    # convert to lowercase to match directory names
    answer_path_lowercase: str = answer_path.lower()

    # include .json file extension to get the question file
    # split to avoid forward slash issues on some os
    file_path_name_strings: List[str] = (answer_path_lowercase + ".json").split("/")
    questions_path: str = os.path.join(root_folder, 'questions', *file_path_name_strings)
    get_file_content: Optional[TQuestionNonPopulated] = open_a_json_file(questions_path)
    return get_file_content


def get_answers_to_template_questions(questions: List[TQuestionPopulated]) -> Optional[Dict[str, str]]:
    """
    Generate a mapping of template questions to their corresponding answers.

    This function takes a list of populated question templates, processes them into
    promptable instances using the `get_inquirer_instance` method, and then
    retrieves user input for these questions through the `inquirer.prompt` function.
    It returns a dictionary containing the answers keyed by the questions' identifiers
    or `None` if no answers are provided.

    :param questions: A list of `TQuestionPopulated` objects containing the
        details of the questions to be asked, such as type and other parameters.
        These details are used to render appropriate prompts.
    :return: A dictionary mapping question identifiers to their corresponding user
        answers, or `None` if no answers were received.
    """

    prompt_questions = [
        get_inquirer_instance(
            question_type=question.get("type", None),
            **question
        )
        for question in questions
    ]
    return inquirer.prompt(prompt_questions)


def generate_executor_file(answer_path: str) -> str:
    # convert to lowercase to match directory names
    answer_path_lowercase: str = answer_path.lower()

    # include .py file extension to get the executor file
    # split to avoid forward slash issues on some os
    file_path_name_strings: List[str] = (answer_path_lowercase + ".py").split("/")
    return os.path.join(root_folder, 'executors', *file_path_name_strings)


def resolve_final_choices(answer_path: str):
    """
    Resolves the final choices given a path to the answers' data. This function
    retrieves information regarding the question and processes the answers for
    template-based questions.

    :param answer_path: A string representing the path to the answers' JSON file.
    :return: None
    """
    question = get_question_json(answer_path)
    template_answers = get_answers_to_template_questions(
        question.get("children", [])
    )
    executor_file = generate_executor_file(answer_path)
    run_python_file(executor_file, template_answers)