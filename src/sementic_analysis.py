import os
import logging
from typing import Dict, List
import libcst as cst
from src.code_extraction import (
    anotherTest, AnotherTestClass
)
import ast

logging.basicConfig(level=logging.ERROR)


def validate_file_path(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"No read permissions for: {file_path}")


def extract_comments(node) -> List[str]:
    comments = []
    if node.trailing_whitespace and hasattr(node.trailing_whitespace, "comments"):
        for comment in node.trailing_whitespace.comments:
            logging.log(f"Comment found: {comment}")
            comments.append(comment.value.strip("# ").strip())
    return comments


def extract_docstring(node) -> str:
    """
    Extracts the docstring from a FunctionDef or ClassDef node.

    Args:
        node: A libcst node (e.g., FunctionDef or ClassDef).

    Returns:
        str or None: The extracted docstring, or None if not found.
    """
    # Ensure the node has a body and the first element is a SimpleStatementLine
    if node.body and isinstance(node.body.body[0], cst.SimpleStatementLine):
        # Get the list of statements in the SimpleStatementLine
        statements = node.body.body[0].body

        # Check if the first statement is a SimpleString (docstring)
        if statements and isinstance(statements[0], cst.SimpleString):
            docstring = statements[0].value  # Extract the value of the SimpleString
            logging.info(f"Docstring found: {docstring}")
            return docstring

    return None


def extract_variables(node) -> List[str]:
    variables = []
    for target in node.targets:
        if isinstance(target.target, cst.Name):
            variables.append(target.target.value)
    return variables


def find_definition_in_file(name, file_path):
    """
    Searches for a class or function definition in a given file.

    Args:
        name (str): The name of the class or function to find.
        file_path (str): Path to the Python file to search.

    Returns:
        str: The source code of the definition if found, otherwise None.
    """
    try:
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read(), filename=file_path)
    except (FileNotFoundError, SyntaxError):
        return None

    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name:
            return ast.unparse(node)  # Requires Python 3.9+
    return None

def resolve_import(import_name, project_root):
    """
    Resolves an import to find the file where the class or function is defined.

    Args:
        import_name (str): The name of the imported module or object.
        project_root (str): Path to the root directory of the project.

    Returns:
        str: The path to the file where the import is defined, or None if not found.
    """
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py") and file[:-3] == import_name:
                return os.path.join(root, file)
    return None

def extract_calls_and_definitions(parsed_ast, target_function, project_root):
    """
    Extracts all function calls, class instantiations, and their definitions from a parsed AST.

    Args:
        parsed_ast (ast.Module): The parsed AST of the target file.
        target_function_name (str): Name of the function to analyze.
        project_root (str): Path to the root directory of the project.

    Returns:
        dict: A dictionary containing:
            - 'function_calls': A list of function calls.
            - 'class_calls': A list of class instantiations and method calls.
            - 'definitions': A dictionary mapping names to their implementations.
    """
    # Lists to store results
    function_calls = []
    class_calls = []
    definitions = {}

    # Step 1: Locate the target function in the parsed AST
    target_function = target_function

    # Step 2: Traverse the target function's AST to find calls
    for sub_node in target_function.body:
        if isinstance(sub_node, ast.Assign):  # Class instantiation (e.g., obj = MyClass())
            for target in sub_node.targets:
                if isinstance(sub_node.value, ast.Call) and isinstance(sub_node.value.func, ast.Name):
                    class_name = sub_node.value.func.id
                    class_calls.append(f"{target.id} = {ast.unparse(sub_node.value)}")

                    # Resolve the class definition
                    definition = None
                    for node in parsed_ast.body:
                        if isinstance(node, ast.ClassDef) and node.name == class_name:
                            definition = ast.unparse(node)
                            break

                    if not definition:
                        # Check imports
                        for imp in parsed_ast.body:
                            if isinstance(imp, ast.ImportFrom):
                                definition = find_definition_in_file(class_name, imp.module.replace('.', '/')+".py")

                    if definition:
                        definitions[class_name] = definition

        elif isinstance(sub_node, ast.Expr) and isinstance(sub_node.value, ast.Call):  # Function or method call
            if isinstance(sub_node.value.func, ast.Attribute):  # Method call (e.g., obj.display())
                class_calls.append(ast.unparse(sub_node.value))
            elif isinstance(sub_node.value.func, ast.Name):  # Function call (e.g., some_function())
                func_name = sub_node.value.func.id
                function_calls.append(ast.unparse(sub_node.value))

                # Resolve the function definition
                definition = None
                for node in parsed_ast.body:
                    if isinstance(node, ast.FunctionDef) and node.name == func_name:
                        definition = ast.unparse(node)
                        break

                if not definition:
                    # Check imports
                    for imp in parsed_ast.body:
                        if isinstance(imp, ast.ImportFrom):
                            definition = find_definition_in_file(func_name, imp.module.replace('.', '/')+".py")


                if definition:
                    definitions[func_name] = definition

    # Step 3: Return the results
    return {
        'functions': function_calls,
        'classes': class_calls,
        'definitions': definitions
    }



def testFun():
    return "testFun"
class TestClass:
    def testFun(self):
        return "test"

def extract_semantic_context_libcst(file_path: str) -> Dict[str, List[str]]:
    """
    Extracts semantic context (comments, docstrings, and variable names) from a Python source file using the libcst library.

    This function reads the source code from the specified file, parses it into an Abstract Syntax Tree (AST) using libcst,
    and extracts the following semantic information:
        - Docstrings: Extracted from function definitions.
        - Comments: Extracted from trailing comments in the source code.
        - Variables: Extracted from assignment statements.

    If any errors occur during the process (e.g., file not found, syntax error), the function logs the error and returns
    a structured error response.

    Parameters:
        file_path (str): The path to the Python source file to be analyzed.

    Returns:
        Union[Dict[str, List[str]], Dict[str, str]]:
            - On success, returns a dictionary with the following keys:
                - 'docstrings': A list of extracted docstrings.
                - 'comments': A list of extracted comments.
                - 'variables': A list of extracted variable names.
            - On failure, returns a dictionary with a single key 'error' containing an error message.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be read due to insufficient permissions.
        cst.ParserSyntaxError: If the source code contains syntax errors that prevent parsing.
        SemanticExtractionError: If an unexpected error occurs during semantic extraction.

    Example Usage:
        >>> result = extract_semantic_context_libcst("example.py")
        >>> print(result)
        {
            'docstrings': ['This is a docstring.'],
            'comments': ['This is a comment.'],
            'variables': ['x', 'y']
        }

    Notes:
        - If a function definition does not contain a docstring, a warning is logged, but no placeholder is added to the output.
        - Large files may cause memory issues if read entirely into memory. Consider processing such files in chunks.
    """

    # default semantic context
    semantic_context = {"docstrings": [], "comments": [], "variables": []}
    # testFun()
    # test = TestClass()
    # test.testFun()

    # test2 = AnotherTestClass()
    # test2.test_method()
    # anotherTest()

    try:
        validate_file_path(file_path)

        with open(file_path, "r") as file:
            source_code = file.read()
        tree = cst.parse_module(source_code)

        class SemanticVisitor(cst.CSTVisitor):
            def visit_SimpleStatementLine(self, node):
                semantic_context["comments"].extend(extract_comments(node))

            def visit_FunctionDef(self, node):
                docstring = extract_docstring(node)
                if docstring:
                    semantic_context["docstrings"].append(docstring)

            def visit_Assign(self, node):
                semantic_context["variables"].extend(extract_variables(node))

        visitor = SemanticVisitor()
        tree.visit(visitor)
        if len(semantic_context["docstrings"]) == 0:
            # If no docstring is found, add a placeholder message
            semantic_context["docstrings"].append(
                "No docstring found. Please provide a docstring."
            )
        return semantic_context

    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
    except PermissionError as e:
        logging.error(f"Permission denied for file: {file_path}")
    except cst.ParserSyntaxError as e:
        logging.error(f"Syntax error in file: {file_path}")
    except Exception as e:
        logging.error(f"Unexpected error in file: {file_path}: {e}")
    return None
