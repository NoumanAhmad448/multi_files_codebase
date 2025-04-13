import ast
import libcst as cst
from collections import defaultdict
# from pycg import CallGraphGenerator
import os
from pathlib import Path
from dotenv import load_dotenv
import git

# Load environment variables from .env file
load_dotenv()
debug = os.getenv("DEBUG", False)

def extract_cross_file_relationships(file_path):
    """Extract cross-file relationships using libcst."""
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
        tree = cst.parse_module(source_code)

        relationships = defaultdict(list)

        class ImportVisitor(cst.CSTVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    relationships["imports"].append(alias.name.value)

            def visit_ImportFrom(self, node):
                module_name = node.module.value
                for alias in node.names:
                    relationships["imports"].append(f"{module_name}.{alias.name.value}")

        visitor = ImportVisitor()
        tree.visit(visitor)
        return dict(relationships)
    except Exception as e:
        print(f"Error extracting cross-file relationships: {e}")
        return None


def analyze_dependencies(file_path):
    try:
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())

        dependencies = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                dependencies.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                dependencies.append(node.module)
        return dependencies
    except Exception as e:
        print(f"Error analyzing dependencies: {e}")
        return []


def calculate_usage_frequency(entry_point, target_file):
    """Calculate how often a file is used in the codebase."""
    cg = CallGraphGenerator([entry_point], "")
    cg.analyze()
    call_graph = cg.output()

    usage_count = 0
    for caller, callees in call_graph.items():
        if target_file in callees:
            usage_count += 1

    return usage_count


def get_file_metadata(file_path):
    """Get metadata about a file."""

    entry_point = os.getenv("MAIN_FILE")

    try:
        file_stats = os.stat(file_path)
        metadata = {
            "file_size": file_stats.st_size,  # Size in bytes
            "file_location": str(Path(file_path).resolve()),  # Absolute path
            "last_modified": file_stats.st_mtime,  # Last modified timestamp
            "usage_frequency": None # calculate_usage_frequency(entry_point, file_path),  # Placeholder for usage frequency
        }
        return metadata
    except Exception as e:
        print(f"Error fetching file metadata: {e}")
        return None


def find_unused_imports(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    imports = set()
    used_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.add(f"{node.module}.{alias.name}" if node.module else alias.name)
        elif isinstance(node, ast.Name):
            used_names.add(node.id)

    unused_imports = imports - used_names
    return list(unused_imports)


def fetch_code_from_branch(repo_path, branch_name, tag_name, commit_hash):
    try:
        print(f"Fetching code from branch: {branch_name}, tag: {tag_name}, commit: {commit_hash}")
        # Open the repository
        repo = git.Repo(repo_path)

        branch = branch_name or tag_name or commit_hash
        # Checkout the specified branch
        if branch:
            repo.git.checkout(branch)
            return True
        return False
    except Exception as e:
        print(f"Error fetching code from branch: {e}")
        return False


def craft_prompt(
    function_name: str,
    issue_description: str,
    request: str,
    dependencies: list,
    function_code: str,
    metadata: dict,
    semantic_info: dict,
    cross_file_relationship: dict,
    categories: str = None,
    CATEGORIES: dict = None
) -> str:
    """
    Crafts a detailed and structured prompt for manual testing on LLMs.

    Args:
        function_name (str): Name of the function being analyzed.
        issue_description (str): Description of the issue or problem.
        request (str): The user's request or query.
        dependencies (list): List of dependencies for the function.
        function_code (str): The actual code of the function.
        metadata (dict): Metadata about the function or file.
        semantic_info (dict): Semantic information (e.g., docstrings, comments).
        cross_file_relationship (dict): Cross-file relationships (e.g., imports, references).
        categories (str, optional): Category key for categorizing the function.
        CATEGORIES (dict, optional): Dictionary mapping category keys to descriptions.

    Returns:
        str: A well-structured prompt string.
    """
    # Initialize the base prompt
    prompt = (
        f"function_name: {function_name}\n"
        f"Issue Description: {issue_description}\n"
        f"Request: {request}\n"
        f"dependencies: {', '.join(dependencies) if dependencies else 'No dependencies detected.'}\n"
        f"function_code:\n{function_code}\n"
        f"metadata:\n"
    )

    # Add metadata
    if metadata:
        for key, value in metadata.items():
            prompt += f"    {key}: {value}\n"
    else:
        prompt += "    No metadata available.\n"

    # Add semantic info
    prompt += "semantic_info:\n"
    if semantic_info:
        for key, value in semantic_info.items():
            prompt += f"    {key}: {value}\n"
    else:
        prompt += "    No semantic information available. Please provide code related semantic information like comments and docstring.\n"

    # Add cross-file relationships
    prompt += "cross_file_relationship:\n"
    if cross_file_relationship:
        for key, value in cross_file_relationship.items():
            prompt += f"    {key}: {', '.join(value) if isinstance(value, list) else value}\n"
    else:
        prompt += "    No cross-file relationships detected.\n"

    # Add categories if provided
    if categories and CATEGORIES:
        category_description = CATEGORIES.get(categories, "Unknown category")
        prompt += f"categories: {category_description}\n"

    return prompt