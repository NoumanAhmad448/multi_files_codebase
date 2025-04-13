from fastapi import FastAPI, HTTPException
from src.code_extraction import extract_function_code
from src.dependency_analysis import (
    analyze_dependencies,
    extract_cross_file_relationships,
    get_file_metadata,
    craft_prompt,
    fetch_code_from_branch,
)
from src.llm_integration import query_llm
from src.sementic_analysis import (
    extract_semantic_context_libcst,
    extract_calls_and_definitions,
)
from app.schemas import UserRequest
from src.load_env import env
import os
from src.constants import CATEGORIES

app = FastAPI()

debug = os.getenv("DEBUG", False)
repo_path = os.getenv("REPO_PATH")


@app.post("/analyze/")
async def analyze_code(request: UserRequest):

    warnings = []

    # Validate request parameters
    if request.categories and not CATEGORIES.get(request.categories):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid category '{request.categories}'. Valid categories are: {', '.join(CATEGORIES.keys())}.",
        )

    # Check if repo_path is provided in the request or environment variable
    if request.repo_path or repo_path:
        git_successuful = (
            fetch_code_from_branch(
                repo_path=request.repo_path or repo_path,
                branch_name=request.branch_name or os.getenv("BRANCH_NAME"),
                tag_name=request.tag_name or os.getenv("TAG_NAME"),
                commit_hash=request.commit_hash or os.getenv("COMMIT_HASH"),
            )
            or os.getenv("COMMIT_HASH"),
        )

        if not git_successuful:
            warnings.append(
                "Failed to fetch code from the specified branch|commit|tag."
            )

    # Extract function code
    function_code, target_function, extract_file = extract_function_code(request.file_path, request.function_name)
    # print(function_code)

    if not function_code:
        raise HTTPException(
            status_code=404,
            detail=f"Function {request.function_name} not found in the specified file {request.file_path}.",
        )

    # unused_imports = find_unused_imports(request.file_path)

    # if unused_imports:
    #         raise HTTPException(
    #             status_code=422,
    #             detail=f"Unused imports found in the specified file: {unused_imports}. Please include them in your code.",
    #         )

    # Analyze dependencies
    dependencies = analyze_dependencies(request.file_path)

    # Semantic Context
    semantic_info = extract_semantic_context_libcst(request.file_path)

    funs_classes = extract_calls_and_definitions(extract_file, target_function, os.getenv("PROJECT_ROOT"))
    # print(funs_classes)

    semantic_info["functions"]  = funs_classes["functions"]
    semantic_info["classes"] = funs_classes["classes"]
    semantic_info["definitions"] = funs_classes["definitions"]

    # Cross-File Relationships
    cross_file_relationship = extract_cross_file_relationships(request.file_path)

    metadata = get_file_metadata(request.file_path)
    request.request = request.request+"""
             You are supposed to take this instruction very carefully and observe
            all the extra parameters provided and make
            a unique optimized decision e.g. if docstring or comments are missing, add them. \n
            """
    # Construct a deep prompt
    prompt = (
        f"function_name: {request.function_name}\n"
        f"issue_description: {request.issue_description}\n"
        f"request: {request.request}\n"
        f"dependencies: {', '.join(dependencies)}\n"
        f"function_code:\n{function_code}\n"
        f"metadata:\n{metadata}\n"
        f"semantic_info:\n{semantic_info}\n"
        f"cross_file_relationship:\n{cross_file_relationship}\n"
    )

    if request.categories:
        prompt += f"categories: {CATEGORIES.get(request.categories)}\n"

    # print(prompt)

    # Query LLM if API key is provided
    if request.api_key:
        llm_response = query_llm(prompt, request.api_key)
        if "error" in llm_response:
            return {"message": "LLM query failed.", "deep_prompt": prompt}
        return {
            "message": "LLM response:",
            "response": llm_response,
            "warnings": warnings,
        }

    # Return deep prompt if no API key is provided

    return {
        "message": "Deep prompt generated for manual refinement.",
        "deep_object": {
            "function_name": request.function_name,
            "issue_description": request.issue_description,
            "request": request.request,
            "dependencies": dependencies,
            "function_code": function_code,
            "metadata": metadata,
            "semantic_info": semantic_info,
            "cross_file_relationship": cross_file_relationship,
            "categories": CATEGORIES.get(request.categories),
        },
        "deep_prompt": craft_prompt(
            request.function_name,
            request.issue_description,
            request.request,
            dependencies,
            function_code,
            metadata,
            semantic_info,
            cross_file_relationship,
            categories=request.categories,
            CATEGORIES=CATEGORIES,
        ),
    }
