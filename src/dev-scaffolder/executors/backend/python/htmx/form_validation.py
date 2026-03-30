import argparse
import os
import sys
from typing import List

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from executors.base import BaseExecutor
from executors.backend.python.django.official import DjangoOfficialExecutor
from executors.backend.python.htmx.official import HtmxOfficialExecutor
from batteries.base import BaseBattery
from batteries.registry import parse_batteries
from typings.base import (
    DjangoOfficialTemplateArgs,
    ExecutorResponseStatus,
)
from utils.base import get_venv_python_executor

HTMX_FORM_VIEWS_PY = """\
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ContactForm


def index(request):
    form = ContactForm()
    return render(request, 'index.html', {'form': form})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            return HttpResponse('<p class="success">&#10003; Message sent successfully!</p>')
        return render(request, 'partials/form.html', {'form': form})
    return render(request, 'partials/form.html', {'form': form})


def validate_field(request, field_name):
    \"\"\"Per-field validation endpoint (hx-trigger=\\"blur\\").\"\"\"
    form = ContactForm({field_name: request.POST.get(field_name, '')})
    form.is_valid()
    errors = form.errors.get(field_name, [])
    if errors:
        return HttpResponse(f'<span class="error">{errors[0]}</span>')
    return HttpResponse('<span class="valid">&#10003;</span>')
"""

HTMX_FORM_FORMS_PY = """\
from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
"""

HTMX_FORM_URLS_PY = """\
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('validate/<str:field_name>/', views.validate_field, name='validate_field'),
]
"""

HTMX_FORM_INDEX_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Contact \u2014 {project_name}{{% endblock %}}
{{% block content %}}
<h1>Contact Form</h1>
<p>This form uses HTMX for submission and inline validation without page reload.</p>
<div id="form-container">
    {{% include "partials/form.html" %}}
</div>
{{% endblock %}}
"""

HTMX_FORM_PARTIAL_HTML = """\
<form hx-post="/contact/" hx-target="#form-container" hx-swap="innerHTML">
    {{% csrf_token %}}
    <div class="field">
        <label>Name</label>
        {{{{ form.name }}}}
        <div class="field-errors">{{{{ form.name.errors }}}}</div>
    </div>
    <div class="field">
        <label>Email</label>
        {{{{ form.email }}}}
        <div class="field-errors">{{{{ form.email.errors }}}}</div>
    </div>
    <div class="field">
        <label>Message</label>
        {{{{ form.message }}}}
        <div class="field-errors">{{{{ form.message.errors }}}}</div>
    </div>
    <button type="submit">Send</button>
</form>
<style>
    .field {{ margin-bottom: 16px; }}
    .field label {{ display: block; font-weight: bold; margin-bottom: 4px; }}
    .field input, .field textarea {{ width: 100%; padding: 8px; box-sizing: border-box; }}
    .error, .field-errors {{ color: red; font-size: 0.9em; }}
    .valid {{ color: green; }}
    .success {{ color: green; font-weight: bold; padding: 16px; }}
    button {{ padding: 8px 16px; }}
</style>
"""


class HtmxFormValidationExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django + HTMX Form Validation project.

    Delegates base project setup to HtmxOfficialExecutor, then adds:
      - forms.py                    — Django ContactForm
      - views.py                    — index, contact, validate_field views
      - urls.py                     — index, contact, validate/<field> routes
      - templates/index.html        — form container with htmx include
      - templates/partials/form.html — form with hx-post + error display

    Supports optional batteries.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django + HTMX Form Validation project.

        :param kwargs:
            - project_name (str): Name of the Django project.
            - directory_name (str): Name of the output directory.
            - app_name (str): Name of the Django app.
        :return: ExecutorResponseStatus indicating success or failure.
        :rtype: ExecutorResponseStatus
        """
        project_name = kwargs['project_name']
        directory_name = kwargs['directory_name']
        app_name = kwargs['app_name']

        htmx_executor = HtmxOfficialExecutor()
        htmx_executor._status = self._status

        self._update_status(f"[bold blue]Scaffolding Django + HTMX project '{project_name}'...[/bold blue]")
        response = htmx_executor.generate(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
            batteries='',
        )

        if not response.success:
            return ExecutorResponseStatus(success=False)

        project_path = response.path
        app_path = os.path.join(project_path, app_name)
        templates_dir = os.path.join(project_path, 'templates')
        partials_dir = os.path.join(templates_dir, 'partials')
        os.makedirs(partials_dir, exist_ok=True)

        self._update_status('[bold blue]Writing forms.py...[/bold blue]')
        with open(os.path.join(app_path, 'forms.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_FORM_FORMS_PY)

        self._update_status('[bold blue]Writing views.py...[/bold blue]')
        with open(os.path.join(app_path, 'views.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_FORM_VIEWS_PY)

        self._update_status('[bold blue]Writing urls.py...[/bold blue]')
        with open(os.path.join(app_path, 'urls.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_FORM_URLS_PY)

        self._update_status('[bold blue]Writing templates/index.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_FORM_INDEX_HTML.format(project_name=project_name))

        self._update_status('[bold blue]Writing templates/partials/form.html...[/bold blue]')
        with open(os.path.join(partials_dir, 'form.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_FORM_PARTIAL_HTML)

        venv_python_executor = get_venv_python_executor()

        for battery in self.batteries:
            battery_name = battery.__class__.__name__
            self._update_status(f'[bold blue]Applying {battery_name}...[/bold blue]')
            install_response = battery.install(venv_python_executor)
            if not install_response.success:
                return ExecutorResponseStatus(success=False)
            battery.configure(project_path, project_name, app_name)

        django_executor = DjangoOfficialExecutor()
        self._update_status('[bold blue]Updating requirements.txt...[/bold blue]')
        django_executor.add_packages_to_requirements_txt(venv_python_executor, project_path)

        self._update_status('[bold blue]Writing README.md...[/bold blue]')
        self._write_readme(project_path, project_name=project_name, app_name=app_name)

        self.console.print(
            f"[bold green]Django + HTMX Form Validation project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Django + HTMX project with inline form validation, '
            'scaffolded with dev-scaffolder.\n\n'
            'Forms are submitted via `hx-post` and field errors are returned as '
            'HTML partials — no page reload required.\n\n'
            '## Requirements\n\n'
            '- Python 3.8+\n\n'
            '## Setup\n\n'
            '```bash\n'
            'python -m venv venv\n'
            'source venv/bin/activate       # macOS / Linux\n'
            'venv\\Scripts\\activate          # Windows\n\n'
            'pip install -r requirements.txt\n'
            '```\n\n'
            '## Run\n\n'
            '```bash\n'
            'python manage.py migrate\n'
            'python manage.py runserver\n'
            '```\n\n'
            'Open http://localhost:8000 in your browser.\n\n'
            '## Endpoints\n\n'
            '- `GET /` — contact form page\n'
            '- `POST /contact/` — submit the form (returns success partial or form with errors)\n'
            '- `POST /validate/<field>/` — per-field validation (for `hx-trigger="blur"`)\n'
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'test') or 'test'
        directory_name = kwargs.get('directory_name', '') or project_name
        app_name = kwargs.get('app_name', '') or 'core'

        batteries_arg = kwargs.get('batteries', '') or ''
        if batteries_arg and not self.batteries:
            self.batteries = parse_batteries(batteries_arg)

        return self.execute_creation_commands(
            project_name=project_name,
            directory_name=directory_name,
            app_name=app_name,
        )

    @classmethod
    def build_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super().build_arg_parser()
        parser.add_argument('--project_name', type=str, default='myproject',
                            help='Name of the Django project')
        parser.add_argument('--directory_name', type=str, default='myproject',
                            help='Name of the project directory')
        parser.add_argument('--app_name', type=str, default='core',
                            help='Name of the Django app')
        parser.add_argument('--batteries', type=str, default='',
                            help='Comma-separated batteries to apply, e.g. "PostgreSQL,Pytest"')
        return parser


def generate_htmx_form_validation_template(**kwargs) -> ExecutorResponseStatus:
    return HtmxFormValidationExecutor().run(**kwargs)


if __name__ == '__main__':
    args = HtmxFormValidationExecutor.build_arg_parser().parse_args()
    HtmxFormValidationExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        app_name=args.app_name,
        batteries=args.batteries,
    )
