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

HTMX_AUTH_FORMS_PY = """\
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
"""

HTMX_AUTH_VIEWS_PY = """\
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import RegisterForm


@login_required
def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponse(
                '<p class="success">Login successful! Redirecting...</p>'
                '<script>setTimeout(() => window.location.href = "/", 500);</script>'
            )
        return HttpResponse('<p class="error">Invalid credentials. Please try again.</p>')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponse(
                '<p class="success">Account created! <a href="/login/">Login here</a></p>'
            )
        return render(request, 'partials/register_form.html', {'form': form})
    return render(request, 'register.html', {'form': form})
"""

HTMX_AUTH_URLS_PY = """\
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
"""

HTMX_AUTH_INDEX_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Home \u2014 {project_name}{{% endblock %}}
{{% block content %}}
<h1>Welcome, {{{{ user.username }}}}!</h1>
<p>You are logged in.</p>
<a href="/logout/">Logout</a>
{{% endblock %}}
"""

HTMX_AUTH_LOGIN_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Login \u2014 {project_name}{{% endblock %}}
{{% block content %}}
<h1>Login</h1>
<div id="login-result"></div>
<form hx-post="/login/" hx-target="#login-result" hx-swap="innerHTML">
    {{% csrf_token %}}
    <div class="field">
        <label>Username</label>
        <input type="text" name="username" required>
    </div>
    <div class="field">
        <label>Password</label>
        <input type="password" name="password" required>
    </div>
    <button type="submit">Login</button>
</form>
<p><a href="/register/">Create an account</a></p>
<style>
    .field {{ margin-bottom: 12px; }}
    .field label {{ display: block; font-weight: bold; margin-bottom: 4px; }}
    .field input {{ width: 100%; max-width: 300px; padding: 8px; box-sizing: border-box; }}
    .error {{ color: red; }}
    .success {{ color: green; }}
    button {{ padding: 8px 16px; margin-top: 8px; }}
</style>
{{% endblock %}}
"""

HTMX_AUTH_REGISTER_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Register \u2014 {project_name}{{% endblock %}}
{{% block content %}}
<h1>Create Account</h1>
<div id="register-form">
    {{% include "partials/register_form.html" %}}
</div>
<p><a href="/login/">Already have an account?</a></p>
{{% endblock %}}
"""

HTMX_AUTH_REGISTER_FORM_PARTIAL = """\
<form hx-post="/register/" hx-target="#register-form" hx-swap="innerHTML">
    {{% csrf_token %}}
    {{% for field in form %}}
    <div class="field">
        <label>{{{{ field.label }}}}</label>
        {{{{ field }}}}
        {{% if field.errors %}}<div class="error">{{{{ field.errors.0 }}}}</div>{{% endif %}}
    </div>
    {{% endfor %}}
    <button type="submit">Register</button>
</form>
<style>
    .field {{ margin-bottom: 12px; }}
    .field label {{ display: block; font-weight: bold; margin-bottom: 4px; }}
    .field input {{ width: 100%; max-width: 300px; padding: 8px; box-sizing: border-box; }}
    .error {{ color: red; font-size: 0.9em; }}
    .success {{ color: green; }}
    button {{ padding: 8px 16px; margin-top: 8px; }}
</style>
"""


class HtmxAuthExecutor(BaseExecutor):
    """
    Executor for scaffolding a Django + HTMX Auth project.

    Delegates base project setup to HtmxOfficialExecutor, then adds:
      - forms.py                              — RegisterForm
      - views.py                              — login, logout, register, index views
      - urls.py                               — login, logout, register, index routes
      - templates/index.html                  — protected home page
      - templates/login.html                  — HTMX login form
      - templates/register.html               — register page
      - templates/partials/register_form.html — register form partial

    The @login_required decorator on index redirects to /login/ automatically.
    Login/register forms use hx-post so no page reload occurs on submit.

    Supports optional batteries.
    """

    def __init__(self, batteries: List[BaseBattery] = None):
        super().__init__()
        self.batteries = batteries or []

    def get_venv_environment(self) -> str:
        return DjangoOfficialExecutor().get_venv_environment()

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        return ExecutorResponseStatus(success=True)

    def _append_login_url_setting(self, settings_path: str) -> None:
        try:
            with open(settings_path, 'a') as f:
                f.write("\nLOGIN_URL = '/login/'\n")
        except FileNotFoundError:
            self.console.print(f'[bold red]Settings file not found: {settings_path}[/bold red]')

    # ------------------------------------------------------------------
    # BaseExecutor lifecycle
    # ------------------------------------------------------------------

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        """
        Scaffolds a Django + HTMX Auth project.

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
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        templates_dir = os.path.join(project_path, 'templates')
        partials_dir = os.path.join(templates_dir, 'partials')
        os.makedirs(partials_dir, exist_ok=True)

        self._update_status('[bold blue]Writing forms.py...[/bold blue]')
        with open(os.path.join(app_path, 'forms.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_AUTH_FORMS_PY)

        self._update_status('[bold blue]Writing views.py...[/bold blue]')
        with open(os.path.join(app_path, 'views.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_AUTH_VIEWS_PY)

        self._update_status('[bold blue]Writing urls.py...[/bold blue]')
        with open(os.path.join(app_path, 'urls.py'), 'w', encoding='utf-8') as f:
            f.write(HTMX_AUTH_URLS_PY)

        self._update_status('[bold blue]Appending LOGIN_URL to settings.py...[/bold blue]')
        self._append_login_url_setting(settings_path)

        self._update_status('[bold blue]Writing templates/index.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_AUTH_INDEX_HTML.format(project_name=project_name))

        self._update_status('[bold blue]Writing templates/login.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'login.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_AUTH_LOGIN_HTML.format(project_name=project_name))

        self._update_status('[bold blue]Writing templates/register.html...[/bold blue]')
        with open(os.path.join(templates_dir, 'register.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_AUTH_REGISTER_HTML.format(project_name=project_name))

        self._update_status('[bold blue]Writing templates/partials/register_form.html...[/bold blue]')
        with open(os.path.join(partials_dir, 'register_form.html'), 'w', encoding='utf-8') as f:
            f.write(HTMX_AUTH_REGISTER_FORM_PARTIAL)

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
            f"[bold green]Django + HTMX Auth project '{project_name}' created successfully![/bold green]"
        )
        return ExecutorResponseStatus(success=True)

    def get_readme_content(self, **kwargs) -> str:
        project_name = kwargs.get('project_name', 'project')
        return (
            f'# {project_name}\n\n'
            'A Django + HTMX project with authentication (login, logout, register), '
            'scaffolded with dev-scaffolder.\n\n'
            'Login and registration forms use HTMX (`hx-post`) for submission — '
            'no full page reload on success or error.\n\n'
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
            '- `GET /` — protected home page (redirects to `/login/` if not authenticated)\n'
            '- `GET/POST /login/` — login form\n'
            '- `GET /logout/` — logout and redirect to login\n'
            '- `GET/POST /register/` — registration form\n'
        )

    def generate(self, **kwargs: DjangoOfficialTemplateArgs) -> ExecutorResponseStatus:
        project_name = kwargs.get('project_name', 'test') or 'test'
        directory_name = kwargs.get('directory_name', '') or project_name
        app_name = kwargs.get('app_name', '') or 'accounts'

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
        parser.add_argument('--app_name', type=str, default='accounts',
                            help='Name of the Django app')
        parser.add_argument('--batteries', type=str, default='',
                            help='Comma-separated batteries to apply, e.g. "PostgreSQL,Pytest"')
        return parser


def generate_htmx_auth_template(**kwargs) -> ExecutorResponseStatus:
    return HtmxAuthExecutor().run(**kwargs)


if __name__ == '__main__':
    args = HtmxAuthExecutor.build_arg_parser().parse_args()
    HtmxAuthExecutor().run(
        project_name=args.project_name,
        directory_name=args.directory_name,
        app_name=args.app_name,
        batteries=args.batteries,
    )
