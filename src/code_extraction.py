import ast


def extract_function_code(file_path, function_name):
    try:
        print(file_path)
        try:
            with open(file_path, "r") as file:
                tree = ast.parse(file.read())
        except SyntaxError as e:
            print(f"Syntax error in file: {e}")
            return None
        print(tree)
        for node in ast.walk(tree):
            print(type(tree))
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return ast.unparse(node),node,tree  # Requires Python 3.9+
        print("here")
        return None
    except Exception as e:
        print(f"Error extracting function: {e}")
        return None


class AnotherTestClass:
    def test_method(self):
        # This is a test method
        return "test2"

def anotherTest():
    return "test"