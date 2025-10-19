# API Documentation
<div align="center">
<img role="button" tabindex="0" id="modal-965287557-trigger" aria-controls="modal-965287557" aria-expanded="false" class="doi-modal-trigger block m-0" src="https://zenodo.org/badge/DOI/10.5281/zenodo.15257762.svg" alt="DOI: 10.5281/zenodo.15257762"></div>

## Overview
This API provides functionality to analyze Python code files based on specific criteria such as function definitions, dependencies, metadata, and semantic context. It supports categorization of code and fetching relevant details to assist in debugging, refactoring, or improving code quality.

---

## Running the Server

To download all the libraries
```bash
pip install -m requirements.txt
```

To start the server, use the following command:

```bash
python -m uvicorn app.main:app --reload
```

- **`app.main`**: Refers to the module (`main.py`) inside the `app` folder where the FastAPI application is defined.
- **`--reload`**: Enables auto-reloading of the server during development.

The server will run locally at:
```
http://127.0.0.1:8000
```

---

## API Endpoint

### POST `/analyze/`

#### Description
Analyzes a specified Python function within a file and provides insights into its structure, dependencies, and relationships.

#### Request Format
Send a JSON payload with the following fields:

| Field               | Type   | Description                                                                 |
|---------------------|--------|-----------------------------------------------------------------------------|
| `function_name`     | String | The name of the function to analyze.                                       |
| `file_path`         | String | Absolute path to the Python file containing the function.                  |
| `issue_description` | String | A description of the issue or problem with the function.                   |
| `request`           | String | What you want from the analysis (e.g., "Suggest improvements").            |
| `categories`        | String | (Optional) A category key to classify the function (e.g., "data_preprocessing"). |

For complete list visit ```schemas.py``` file and check ```UserRequest```
POV: ```Please note that .env file is being used however it doesn't get proritized over API params. You have a choice to mention either use
.env file or you may pass params.```

#### Example Request

Use the following `curl` command to test the API:

```bash
curl -X POST "http://127.0.0.1:8000/analyze/" \
-H "Content-Type: application/json" \
-d '{
  "function_name": "extract_semantic_context_libcst",
  "file_path": "B:/multi_files_codebase/multi_files_codebase/src//sementic_analysis.py",
  "issue_description": "The function lacks error handling.",
  "request": "Suggest improvements for this function.",
  "categories": "data_preprocessing"
}'
```

---

## Sample Input and Output

### Input

```json
{
  "function_name": "extract_semantic_context_libcst",
  "file_path": "B:/multi_files_codebase/src/sementic_analysis.py",
  "issue_description": "The function lacks error handling.",
  "request": "Suggest improvements for this function.",
  "categories": "data_preprocessing"
}
```

### Response

If the request is successful, the API will return a structured response with the following details:

```json
{
  "function_name": "extract_semantic_context_libcst",
  "file_path": "B:/multi_files_codebase/src/sementic_analysis.py",
  "issue_description": "The function lacks error handling.",
  "request": "Suggest improvements for this function.",
  "dependencies": ["libcst", "ast"],
  "function_code": "def extract_semantic_context_libcst():\n    pass",
  "metadata": {
    "file_size": "4096 bytes",
    "file_location": "B:/multi_files_codebase/src/sementic_analysis.py",
    "last_modified": "2023-10-05T14:23:45Z"
  },
  "semantic_info": {
    "docstring": "Extracts semantic context using libcst.",
    "comments": ["TODO: Add error handling"]
  },
  "cross_file_relationship": {
    "imports": ["libcst", "os"],
    "referenced_in": ["main.py", "utils.py"]
  },
  "categories": "Code related to data preprocessing and transformation."
}
```

---

## Notes

1. **File Path**:
   - Ensure the `file_path` is an absolute path to the Python file.
   - Use forward slashes (`/`) or double backslashes (`\\`) for Windows paths.

2. **Categories**:
   - The `categories` field is optional. If provided, it should match predefined category keys (e.g., `data_preprocessing`, `api_endpoints`).

3. **Error Handling**:
   - If the `file_path` is invalid or the `function_name` does not exist, the API will return an appropriate error message.

---

## Troubleshooting

### Common Issues

#### 1. **File Not Found**
If the file path is incorrect, you may see:
```json
{
  "error": "File not found: B:/multi_files_codebase/src/sementic_analysis.py"
}
```

#### 2. **Function Not Found**
If the specified function does not exist in the file, you may see:
```json
{
  "error": "Function 'extract_semantic_context_libcst' not found in the file."
}
```

#### 3. **Invalid JSON Payload**
Ensure the JSON payload is valid. For example, missing commas or quotes can cause parsing errors.

---

## Conclusion

This API simplifies the process of analyzing Python functions by extracting their code, dependencies, metadata, and relationships. Use the provided examples and troubleshooting tips to integrate it into your workflow effectively.

Let me know if you need further refinements! 🚀

## 📖 Citation

If you use this codebase in your research or projects, please cite it as follows:

### 🔹 BibTeX
```@INPROCEEDINGS{11182836,
  author={Ahmad, Nouman and Zhang, Changsheng},
  booktitle={2025 5th International Conference on Artificial Intelligence, Big Data and Algorithms (CAIBDA)}, 
  title={Enhancing LLMs Interactions for Python: A Smart API Framework for Extracting and Utilizing Semantic Code Information}, 
  year={2025},
  volume={},
  number={},
  pages={385-388},
  keywords={Measurement;Codes;Navigation;Large language models;Semantics;Manuals;Metadata;Data mining;Prompt engineering;Software development management;Prompt Engineering;Semantic Code Analysis;LLM Interactions},
  doi={10.1109/CAIBDA65784.2025.11182836}}
```

### 🔹 EndNote (RIS)
```TY  - CONF
TI  - Enhancing LLMs Interactions for Python: A Smart API Framework for Extracting and Utilizing Semantic Code Information
T2  - 2025 5th International Conference on Artificial Intelligence, Big Data and Algorithms (CAIBDA)
SP  - 385
EP  - 388
AU  - N. Ahmad
AU  - C. Zhang
PY  - 2025
DO  - 10.1109/CAIBDA65784.2025.11182836
JO  - 2025 5th International Conference on Artificial Intelligence, Big Data and Algorithms (CAIBDA)
IS  - 
SN  - 
VO  - 
VL  - 
JA  - 2025 5th International Conference on Artificial Intelligence, Big Data and Algorithms (CAIBDA)
Y1  - 20-22 June 2025
ER  - 
```

