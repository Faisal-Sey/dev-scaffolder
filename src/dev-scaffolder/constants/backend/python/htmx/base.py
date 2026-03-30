# ── Shared / Official ─────────────────────────────────────────────────────────

HTMX_CDN_SCRIPT = '<script src="https://unpkg.com/htmx.org@2.0.3"></script>'

HTMX_BASE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{project_name}{{% endblock %}}</title>
    <script src="https://unpkg.com/htmx.org@2.0.3"></script>
    {{% block extra_head %}}{{% endblock %}}
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
        button {{ padding: 8px 16px; cursor: pointer; }}
        #result {{ margin-top: 16px; padding: 12px; background: #f0f0f0; border-radius: 4px; min-height: 40px; }}
    </style>
</head>
<body>
    {{% block content %}}{{% endblock %}}
</body>
</html>
"""

HTMX_INDEX_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Home — {project_name}{{% endblock %}}
{{% block content %}}
<h1>{project_name}</h1>
<p>A Django + HTMX project. Click the button to fetch a server response without a page reload.</p>
<button hx-get="/demo/" hx-target="#result" hx-swap="innerHTML" hx-indicator="#spinner">
    Fetch from server
</button>
<span id="spinner" class="htmx-indicator"> ⏳</span>
<div id="result"></div>
{{% endblock %}}
"""

HTMX_DEMO_PARTIAL_HTML = """\
<p>Server responded at <strong>{{ timestamp }}</strong></p>
"""

HTMX_VIEWS_PY = """\
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone


def index(request):
    return render(request, 'index.html')


def demo(request):
    timestamp = timezone.now().strftime('%H:%M:%S')
    return HttpResponse(f'<p>Server responded at <strong>{timestamp}</strong></p>')
"""

HTMX_APP_URLS_PY = """\
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('demo/', views.demo, name='demo'),
]
"""

# ── Alpine JS ─────────────────────────────────────────────────────────────────

HTMX_ALPINE_BASE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{project_name}{{% endblock %}}</title>
    <script src="https://unpkg.com/htmx.org@2.0.3"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    {{% block extra_head %}}{{% endblock %}}
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
        button {{ padding: 8px 16px; cursor: pointer; margin: 4px; }}
        .card {{ padding: 16px; background: #f0f0f0; border-radius: 4px; margin-top: 16px; }}
    </style>
</head>
<body>
    {{% block content %}}{{% endblock %}}
</body>
</html>
"""

HTMX_ALPINE_INDEX_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Home — {project_name}{{% endblock %}}
{{% block content %}}
<h1>{project_name}</h1>
<p>A Django + HTMX + Alpine.js project.</p>

<h2>HTMX — Server fetch</h2>
<button hx-get="/demo/" hx-target="#htmx-result" hx-swap="innerHTML">
    Fetch from server
</button>
<div id="htmx-result" class="card"></div>

<h2>Alpine.js — Client-side counter</h2>
<div x-data="{ count: 0 }" class="card">
    <p>Count: <strong x-text="count"></strong></p>
    <button @click="count++">Increment</button>
    <button @click="count = 0">Reset</button>
</div>
{{% endblock %}}
"""

# ── Tailwind CSS ──────────────────────────────────────────────────────────────

HTMX_TAILWIND_BASE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{project_name}{{% endblock %}}</title>
    <script src="https://unpkg.com/htmx.org@2.0.3"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    {{% block extra_head %}}{{% endblock %}}
</head>
<body class="bg-gray-50 text-gray-900">
    <div class="max-w-2xl mx-auto px-4 py-10">
        {{% block content %}}{{% endblock %}}
    </div>
</body>
</html>
"""

HTMX_TAILWIND_INDEX_HTML = """\
{{% extends "base.html" %}}
{{% block title %}}Home — {project_name}{{% endblock %}}
{{% block content %}}
<h1 class="text-3xl font-bold mb-4">{project_name}</h1>
<p class="text-gray-600 mb-6">A Django + HTMX + Tailwind CSS project.</p>

<button
    hx-get="/demo/"
    hx-target="#result"
    hx-swap="innerHTML"
    class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
>
    Fetch from server
</button>

<div id="result" class="mt-4 p-4 bg-white rounded shadow min-h-[48px]"></div>
{{% endblock %}}
"""
