import libcst as cst


def extract_semantic_context_libcst(file_path):
    """Extract comments, docstrings, and variable names using libcst."""
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
        tree = cst.parse_module(source_code)

        semantic_context = {"docstrings": [], "comments": [], "variables": []}

        class SemanticVisitor(cst.CSTVisitor):
            def visit_SimpleStatementLine(self, node):
                for comment in node.trailing_whitespace.comments:
                    semantic_context["comments"].append(
                        comment.value.strip("# ").strip()
                    )

            def visit_FunctionDef(self, node):
                if node.body and isinstance(node.body.body[0], cst.SimpleStatementLine):
                    docstring = node.body.body[0].body[0].value.value
                    semantic_context["docstrings"].append(docstring)

            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target.target, cst.Name):
                        semantic_context["variables"].append(target.target.value)

        visitor = SemanticVisitor()
        tree.visit(visitor)
        return semantic_context
    except Exception as e:
        print(f"Error extracting semantic context: {e}")
        return None
