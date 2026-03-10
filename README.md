# Project Scaffolder

A dynamic, interactive CLI-based project generator that simplifies the process of scaffolding new projects through a tree-based question system and custom template executors.

## Features

- **Interactive Question Tree**: Navigate through a logical hierarchy of choices defined in JSON.
- **Extensible Architecture**: Easily add new templates and questions by adding JSON files and Python executors.
- **Styled CLI Output**: Uses `rich` to provide a clean and professional command-line interface with panels, colors, and spinners.
- **Robust Input Handling**: Powered by `inquirer` for intuitive selections and confirmations.
- **Environment-Aware Output**: Projects and virtual environments are created in `temp/` during development, keeping generated files out of version control.
- **Base Executor Pattern**: All executors inherit from `BaseExecutor`, which provides a consistent lifecycle and a built-in loading spinner that automatically pauses around interactive prompts.

## Installation

### Prerequisites

- Python 3.8+

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd template
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment by creating a `.env` file in the project root:
   ```env
   ENVIRONMENT=development
   ```
   Accepted values: `development`, `production`.

## Usage

To start the project generation process, run the main scaffolder script:

```bash
python scripts/scaffolder/scaffolder.py
```

Follow the on-screen prompts to select your project type, language, and other configurations.

## Project Structure

```
template/
├── .env                   # Environment configuration (ENVIRONMENT=development|production)
├── questions/             # JSON files defining the question hierarchy
├── executors/             # Executor classes for each supported framework
│   ├── base.py            # BaseExecutor abstract class (lifecycle + spinner)
│   └── backend/
│       └── python/
│           └── django/    # Django-specific executors
├── processors/            # Core logic: question loading, input handling, template resolution
├── utils/
│   ├── base.py            # Subprocess, file, and venv utilities
│   └── env.py             # Environment detection and path resolution
├── constants/             # Framework-specific code snippets and configuration strings
├── typings/               # Shared type definitions and dataclasses
└── scripts/               # Entry points for running the scaffolder
```

## How It Works

1. **Question Loading**: The system starts by loading `questions/base.json`.
2. **Dynamic Traversal**: Based on user selection, it recursively loads child questions from the file system.
3. **Template Resolution**: Once a leaf node (a final choice) is reached, the system identifies the corresponding executor in the `executors/` directory.
4. **Execution**: The executor's `run()` method is called with the gathered parameters. It starts a loading spinner, delegates to `generate()`, and stops the spinner when done.

## Environment Modes

The `ENVIRONMENT` variable in `.env` controls where generated output is placed.

| `ENVIRONMENT` | Project output | Virtual environment |
|---|---|---|
| `development` | `<project_root>/temp/` | `<project_root>/temp/venv/` |
| `production` | Current working directory | `<project_root>/venv/` |

The `temp/` directory is listed in `.gitignore` so development output is never committed.

## Executor Architecture

All executors inherit from `BaseExecutor` (`executors/base.py`) and must implement:

| Method | Purpose |
|---|---|
| `get_venv_environment()` | Set up and return the venv Python path |
| `install_dependencies(venv_python_executor)` | Install framework packages |
| `execute_creation_commands(**kwargs)` | Orchestrate the full scaffold |
| `generate(**kwargs)` | Resolve arguments and drive the above steps |

`prepare_directory()` is provided as a concrete default on `BaseExecutor` — it creates the output directory or prompts the user to replace it if one already exists. Override it only if the executor needs different behaviour.

The public entry point is `run(**kwargs)`, which wraps `generate()` with a `rich` loading spinner. Use `self._stop_status()` / `self._start_status()` around any interactive `inquirer` prompts inside your executor to prevent the spinner from blocking user input. Use `self._update_status(message)` to update the spinner label as execution progresses through steps.

### Adding a New Executor

1. Create a JSON file in `questions/` defining the configuration options for the new template.
2. Link it to the existing question tree via `questions/base.json`.
3. Create a Python file in the corresponding `executors/` path and subclass `BaseExecutor`:

```python
from executors.base import BaseExecutor
from typings.base import ExecutorResponseStatus

class MyFrameworkExecutor(BaseExecutor):

    def get_venv_environment(self) -> str:
        ...

    def install_dependencies(self, venv_python_executor: str) -> ExecutorResponseStatus:
        ...

    def execute_creation_commands(self, **kwargs) -> ExecutorResponseStatus:
        ...

    def generate(self, **kwargs):
        ...

if __name__ == '__main__':
    args = MyFrameworkExecutor.build_arg_parser().parse_args()
    MyFrameworkExecutor().run(**vars(args))
```

## Contributing

### Branching

- `main` — stable branch; only merge via pull request
- Feature branches should follow the pattern: `feature/<short-description>` (e.g. `feature/fastapi-executor`)
- Bug fix branches: `fix/<short-description>` (e.g. `fix/venv-path-dev-mode`)

### Workflow

1. Fork or branch from `main`:
   ```bash
   git checkout -b feature/<short-description>
   ```

2. Set up your environment:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env   # set ENVIRONMENT=development
   ```

3. Make your changes following the conventions below, then commit:
   ```bash
   git add <files>
   git commit -m "feat: short description of change"
   ```

4. Push and open a pull request against `main`.

### Adding a Question

Questions live in `questions/` as JSON files and mirror the `executors/` directory structure. Each file defines a node in the question tree:

```json
{
  "type": "list",
  "name": "my_option",
  "message": "Choose an option",
  "choices": ["Option A", "Option B"],
  "children": []
}
```

Leaf nodes (no children) trigger executor resolution — the scaffolder maps the answer path directly to a file in `executors/`.

### Adding an Executor

Follow the steps in [Adding a New Executor](#adding-a-new-executor) above. Additional conventions:

- Place the file at `executors/<category>/<language>/<framework>/<name>.py` to match the question path.
- Use `self.console` for all terminal output — never use `print()`.
- Use `self._update_status(message)` to label each distinct step in `execute_creation_commands`.
- Call `self._stop_status()` before any `inquirer.prompt()` and `self._start_status()` immediately after.
- All subprocess calls must use the venv Python executor (`get_venv_python_executor()`) rather than bare shell commands, so they work correctly in both `development` and `production` environments.

### Code Style

- Follow PEP 8.
- All public methods must have docstrings with `:param:` and `:return:` annotations.
- Keep `utils/` functions generic and stateless — executor-specific logic belongs in the executor class.