"""
repo_structure.py

Example module for cloning a GitHub repo, traversing its file structure,
and returning a JSON-friendly nested directory tree. Includes constants
for exclude patterns by project type.
"""

import os
import json
import git
from pathlib import Path
from pathspec import PathSpec
from alive_progress import alive_bar

from clone_progress import CloneProgress

###################################
# EXCLUDE PATTERN CONSTANTS
###################################

# Default exclude patterns that are useful for virtually any repo
DEFAULT_EXCLUDES = [
    ".git",            # Git repository folder
    "node_modules",    # Node.js packages
    "venv",            # Python virtual env
]

# Language/Framework-specific ignore patterns
# (You might expand these lists as needed for your projects)
PYTHON_EXCLUDES = [
    "__pycache__",
    "*.pyc",
    ".idea",
    ".vscode",
    # You can add more Python-related directories/files here
]

NODE_EXCLUDES = [
    "dist",
    "build",
    ".idea",
    ".vscode",
    "coverage",
    # You can add more Node-related directories/files here
]

JAVA_EXCLUDES = [
    "target",
    "out",
    "build",
    ".idea",
    ".vscode",
    # You can add more Java/Gradle/Maven directories/files here
]

# Combine project-specific excludes with defaults
PROJECT_EXCLUDES = {
    "python": list(set(DEFAULT_EXCLUDES + PYTHON_EXCLUDES)),
    "node": list(set(DEFAULT_EXCLUDES + NODE_EXCLUDES)),
    "java": list(set(DEFAULT_EXCLUDES + JAVA_EXCLUDES)),
}

###################################
# REPO STRUCTURE LOGIC
###################################

def get_repo_structure(
    github_url: str,
    clone_path: str = None,
    token: str = None,
    max_depth: int = None,
    exclude_patterns=None
):
    """
    Clones a GitHub repo (if not already cloned) and returns its directory structure
    up to a specified depth (max_depth). Also uses .gitignore plus any extra exclude
    patterns to skip certain files/folders. Ignores symlinks.

    :param github_url: URL of the GitHub repository, e.g. "https://github.com/org/repo.git"
    :param clone_path: Local path to clone the repo. If it already has .git, we won't reclone.
    :param token: GitHub personal access token (if needed for private repos).
    :param max_depth: Max depth to recursively explore (0 => top-level only). None => no limit.
    :param exclude_patterns: Optional list of folder or file names (globs) to exclude.
    :return: A nested dictionary representing the directory structure.
    """
    # If no exclude_patterns were provided, just use DEFAULT_EXCLUDES
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDES
    else:
        # Combine user-provided excludes with our defaults
        exclude_patterns = list(set(exclude_patterns + DEFAULT_EXCLUDES))

    # 1) Clone the repo if needed
    repo_path = _clone_repo_if_needed(github_url, clone_path, token)

    # 2) Parse .gitignore (if present)
    pathspec_obj = _get_pathspec(repo_path)

    # 3) Build the tree starting from repo root
    structure = _build_tree(
        current_path=repo_path,
        repo_root=repo_path,
        pathspec_obj=pathspec_obj,
        max_depth=max_depth,
        current_depth=0,
        exclude_patterns=exclude_patterns
    )

    return structure

def clone_repo_with_progress(github_url, clone_path, token=None):
    """
    Clones a GitHub repo to the specified path with an alive-progress spinner.
    If a token is provided for a private repo, we'll insert it into the URL.
    """
    # If token is provided, modify the URL to include it (assuming https://).
    if token:
        if not github_url.startswith("https://"):
            raise ValueError("Token-based clone requires an https:// URL.")
        prefix = "https://"
        url_without_prefix = github_url[len(prefix):]  # e.g. "github.com/org/repo.git"
        authed_url = f"{prefix}{token}@{url_without_prefix}"
    else:
        authed_url = github_url

    progress_handler = CloneProgress()

    # We wrap the clone operation in a `with alive_bar(...) as bar:` context
    # so that the bar is properly closed when done (or if an error occurs).
    with alive_bar(title=f"Cloning {github_url}", spinner="dots") as bar:
        progress_handler.set_bar(bar)
        repo = git.Repo.clone_from(authed_url, clone_path, progress=progress_handler)
    
    return repo

def _clone_repo_if_needed(github_url, clone_path, token):
    """
    Uses clone_repo_with_progress(...) if the path is not already cloned.
    """
    repo_path = Path(clone_path)
    git_folder = repo_path / ".git"

    if repo_path.exists() and git_folder.exists():
        print(f"Repository already cloned at: {repo_path}")
        return repo_path
    else:
        print(f"Cloning repository from {github_url} into {repo_path}")
        clone_repo_with_progress(github_url, repo_path, token=token)
        return repo_path

def _get_pathspec(repo_path):
    """
    Reads .gitignore (if present) from the root of `repo_path` and returns a
    compiled pathspec object. If no .gitignore is found, returns None.
    """
    gitignore_file = repo_path / ".gitignore"
    if not gitignore_file.is_file():
        return None

    with gitignore_file.open("r") as f:
        gitignore_lines = f.readlines()

    # Use Git's wildcard matching
    return PathSpec.from_lines("gitwildmatch", gitignore_lines)

def _is_ignored(path, pathspec_obj, repo_root):
    """
    Returns True if the file/folder at `path` is ignored according to .gitignore.
    If pathspec_obj is None, we return False. Compares the relative path.
    """
    if pathspec_obj is None:
        return False

    rel_str = str(path.relative_to(repo_root))
    return pathspec_obj.match_file(rel_str)

def _build_tree(
    current_path: Path,
    repo_root: Path,
    pathspec_obj: PathSpec,
    max_depth: int,
    current_depth: int,
    exclude_patterns
):
    """
    Recursively builds a JSON-like tree representing the repo structure.
    - Directories and files that match .gitignore or the exclude list are skipped.
    - Symlinks are ignored.
    - Returns directories first (alphabetically) then files (alphabetically).
    - If type="file", omits "children". If a directory has no children, omits "children".
    """

    # If max_depth=0, return only current level (no children).
    # If max_depth=1, return current + one level below, etc.
    if max_depth is not None and current_depth > max_depth:
        return None

    # Check if any part of the path is in exclude_patterns
    if any(part in exclude_patterns for part in current_path.parts):
        return None

    # Check if .gitignore excludes this path
    if _is_ignored(current_path, pathspec_obj, repo_root):
        return None

    # Ignore symlinks
    if current_path.is_symlink():
        return None

    # If this is a file
    if current_path.is_file():
        return {
            "name": current_path.name,
            "type": "file"
        }

    # If this is a directory
    if current_path.is_dir():
        node = {
            "name": current_path.name,
            "type": "directory"
        }

        # If we're at exactly max_depth, don't gather children.
        # Only gather if current_depth < max_depth (or if max_depth is None).
        if max_depth is None or current_depth < max_depth:
            dirs = []
            files = []
            for entry in current_path.iterdir():
                if entry.is_dir():
                    dirs.append(entry)
                else:
                    files.append(entry)

            # Sort directories and files by name (case-insensitive)
            dirs.sort(key=lambda d: d.name.lower())
            files.sort(key=lambda f: f.name.lower())

            children = []
            for d in dirs:
                child_node = _build_tree(
                    d,
                    repo_root,
                    pathspec_obj,
                    max_depth,
                    current_depth + 1,
                    exclude_patterns
                )
                if child_node is not None:
                    children.append(child_node)

            for f in files:
                child_node = _build_tree(
                    f,
                    repo_root,
                    pathspec_obj,
                    max_depth,
                    current_depth + 1,
                    exclude_patterns
                )
                if child_node is not None:
                    children.append(child_node)

            if children:
                node["children"] = children

        return node

    # Special case: neither file nor directory (e.g., device file on unusual OS)
    return None
