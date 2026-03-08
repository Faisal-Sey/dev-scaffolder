import sys
import os
import inquirer
from typing import Optional, Dict, List

# Add project root to sys.path to resolve internal modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from processors.load_questions import load_questions
from processors.get_inquirer import get_inquirer_instance
from processors.handle_answers import resolve_final_choices
from utils.base import clean_name, build_answers_path


def run_scaffolder():
    """
    Main loop for the scaffolder. Navigates through a tree of questions
    and resolves the final choices once a leaf node is reached.
    """
    current_question = load_questions()
    if not current_question:
        print("Questions not configured")
        return

    answers_path = ""

    while True:
        # Prompt the current question
        prompt = [
            get_inquirer_instance(
                question_type=current_question.get("type"),
                **current_question
            )
        ]
        
        answers: Optional[Dict[str, str]] = inquirer.prompt(prompt)
        
        # If the user cancels (e.g., Ctrl+C), answers will be None
        if not answers:
            print("No answer was selected")
            break

        current_answer = answers.get(current_question.get("name"))
        if current_answer is None:
            print("No answer was selected")
            break

        # Update the logical path of selected answers
        answers_path = build_answers_path(answers_path, current_answer)

        # Look for the next question in the children list
        children: List[Dict] = current_question.get("children", [])
        cleaned_answer = clean_name(current_answer)
        
        next_question = next(
            (q for q in children if q.get("name") == cleaned_answer),
            None
        )

        # If no child matches the answer, we've reached a leaf node
        if next_question is None:
            resolve_final_choices(answers_path)
            break

        current_question = next_question


if __name__ == "__main__":
    run_scaffolder()