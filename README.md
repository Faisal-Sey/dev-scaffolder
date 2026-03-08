# Project Scaffolder

A dynamic, interactive CLI-based project generator that simplifies the process of scaffolding new projects through a tree-based question system and custom template executors.

## 🚀 Features

- **Interactive Question Tree**: Navigate through a logical hierarchy of choices defined in JSON.
- **Extensible Architecture**: Easily add new templates and questions by adding JSON files and Python executors.
- **Styled CLI Output**: Uses `rich` to provide a clean and professional command-line interface with panels, colors, and progress indicators.
- **Robust Input Handling**: Powered by `inquirer` for intuitive selections and confirmations.
- **Automatic Environment Management**: Built-in support for checking and creating virtual environments for template execution.

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- [Optional] Node.js (if using the JS-based scaffolder)

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

## 📖 Usage

To start the project generation process, run the main scaffolder script:

```bash
python scripts/scaffolder/scaffolder.py
```

Follow the on-screen prompts to select your project type, language, and other configurations.

## 📂 Project Structure

- `questions/`: Contains JSON files defining the hierarchy of questions and their possible answers.
- `executors/`: Contains Python scripts responsible for the actual project creation and configuration.
- `processors/`: Core logic for loading questions, handling user input, and resolving templates.
- `utils/`: Common utility functions for file operations, subprocess execution, and environment setup.
- `scripts/`: Entry points for running the scaffolder (Python and JavaScript versions).
- `typings/`: Type definitions for project consistency and better developer experience.

## ⚙️ How It Works

1. **Question Loading**: The system starts by loading `questions/base.json`.
2. **Dynamic Traversal**: Based on user selection, it recursively loads child questions from the file system.
3. **Template Resolution**: Once a leaf node (a final choice) is reached, the system identifies the corresponding executor script in the `executors/` directory.
4. **Execution**: The executor script is run with the gathered parameters to generate the actual project files.

## 🎨 Customization

To add a new project template:
1. Create a new JSON file in `questions/` defining the configuration options.
2. Link it to the existing question tree in `questions/base.json`.
3. Create a corresponding Python script in `executors/` that implements the logic for creating the project.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
