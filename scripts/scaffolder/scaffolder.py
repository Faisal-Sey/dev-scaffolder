import copy
import sys
import os
import inquirer

from typing import Optional, Dict

# Add project root to sys.path
# Fix - ModuleNotFoundError: No module named 'processor'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typings.question import TQuestionPopulated

from processors.load_questions import load_questions
from processors.get_inquirer import get_inquirer_instance
from processors.handle_answers import resolve_final_choices
from utils.base import clean_name, build_answers_path


questions: Optional[TQuestionPopulated] = load_questions()
next_question = copy.deepcopy(questions) # initialize questions
is_running = True
answers_path = ""

if questions is not None:
    while is_running:
        prompt_questions = [
            get_inquirer_instance(
                question_type=next_question.get("type", None),
                **next_question
            )
        ]
        answers: Optional[Dict[str, str]] = inquirer.prompt(prompt_questions)
        if answers is None:
            print("No answer was selected")
            is_running = False
            break

        current_question_answer: Optional[str] = answers.get(next_question.get("name"), None)
        answers_path = build_answers_path(answers_path, current_question_answer)

        if current_question_answer is None:
            print("No answer was selected")
            is_running = False
            break

        found_question = next(
            filter(
                lambda question: question.get("name") == clean_name(current_question_answer),
                next_question.get("children", [])
            ),
            None
        )

        if found_question is None:
            resolve_final_choices(answers_path)
            is_running = False
            break

        next_question = found_question
        # is_running = False

else:
    print("Questions not configured")