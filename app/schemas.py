from pydantic import BaseModel


class UserRequest(BaseModel):
    function_name: str
    file_path: str
    issue_description: str
    request: str
    api_key: str = None
    repo_path: str = None
    branch_name: str = None
    tag_name: str = None
    commit_hash: str = None
    categories: str = None
