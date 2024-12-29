# GitHub Repository Structure Analyzer

A Python utility for cloning GitHub repositories and generating a JSON-friendly representation of their directory structure. This tool provides a clean way to analyze repository layouts while respecting `.gitignore` rules and offering customizable exclude patterns for different project types.

## Features

- Clone GitHub repositories with progress visualization
- Generate nested JSON representation of repository structure
- Support for private repositories via GitHub tokens
- Respect `.gitignore` patterns
- Configurable depth limit for directory traversal
- Pre-defined exclude patterns for common project types (Python, Node.js, Java)
- Progress bar visualization during cloning using `alive-progress`
- Handles symlinks and special files appropriately

## Installation

### Prerequisites

Make sure you have Python 3.6+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from repo_structure import get_repo_structure

# Simple example with default settings
structure = get_repo_structure(
    github_url="https://github.com/username/repo.git",
    clone_path="local_repo_folder"
)
```

### Advanced Usage

```python
from repo_structure import get_repo_structure, PROJECT_EXCLUDES
import json

# Using project-specific excludes and depth limit
structure = get_repo_structure(
    github_url="https://github.com/username/repo.git",
    clone_path="local_repo_folder",
    token="your_github_token",  # For private repos
    max_depth=2,  # Limit directory traversal depth
    exclude_patterns=PROJECT_EXCLUDES["python"]  # Use Python-specific excludes
)

# Print the structure as formatted JSON
print(json.dumps(structure, indent=2))
```

### Private Repositories

For private repositories, you'll need to provide a GitHub personal access token:

```python
structure = get_repo_structure(
    github_url="https://github.com/oguzhancetinkaya/private-repo.git",
    clone_path="private_repo_folder",
    token="your_github_personal_access_token"
)
```

## Exclude Patterns

The tool comes with predefined exclude patterns for different project types:

- `DEFAULT_EXCLUDES`: Basic patterns like `.git`, `node_modules`, `venv`
- `PYTHON_EXCLUDES`: Python-specific patterns
- `NODE_EXCLUDES`: Node.js-specific patterns
- `JAVA_EXCLUDES`: Java-specific patterns

You can also provide your own custom exclude patterns:

```python
custom_excludes = [
    "*.log",
    "temp",
    "custom_folder"
]

structure = get_repo_structure(
    github_url="https://github.com/username/repo.git",
    clone_path="local_repo_folder",
    exclude_patterns=custom_excludes
)
```

## Output Format

The tool generates a nested dictionary structure that represents the repository layout:

```json
{
  "name": "repo_name",
  "type": "directory",
  "children": [
    {
      "name": "src",
      "type": "directory",
      "children": [
        {
          "name": "main.py",
          "type": "file"
        }
      ]
    }
  ]
}
```

## Components

### repo_structure.py

The main module containing:

- Directory traversal logic
- Repository cloning functionality
- Exclude pattern definitions
- `.gitignore` integration

### clone_progress.py

A helper module that provides:

- Custom progress handler for Git operations
- Integration with the `alive-progress` library
- Visual feedback during repository cloning

## Contributing

Contributions are welcome! Some areas for potential improvement:

- Additional project-type exclude patterns
- Support for other Git hosting services
- Enhanced progress reporting
- Additional output formats
- Performance optimizations for large repositories

## License

[Add your chosen license here]

---

## License

This project is open-source. See the [LICENSE](vscode-file://vscode-app/private/var/folders/d_/1hbc6cs172n3vqy5vm8_jjcm0000gn/T/AppTranslocation/565C53E6-A178-4D77-8626-F09590BD7FD3/d/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) file for details.

---

Thank you for using **github-repo-structure** ! If you have any questions or suggestions, don’t hesitate to create an issue or open a discussion. Happy coding! ```
