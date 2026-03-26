from typing import Union

import inquirer

InstanceTypes = Union[
    inquirer.Text,
    inquirer.List,
    inquirer.Confirm,
    inquirer.Checkbox,
    inquirer.Editor
]

def get_inquirer_instance(question_type: str, **kwargs) -> InstanceTypes:
    """
    Dynamically create an inquirer question

    Args:
        question_type: Question type
        **kwargs: Additional arguments specific to a question type
    """
    inquirer_instance = getattr(inquirer, question_type.title())

    # remove non-required fields - check typings/question.py for structure
    non_required = [
        "type",
        "children"
    ]

    for field in non_required:
        kwargs.pop(field, None)

    return inquirer_instance(**kwargs)