from tools.mcp_server import (
    read_coding_guidelines, get_repo_structure, get_files, apply_edits,
    run_test_suite,get_repository_diff, fetch_github_issue, publish_pull_request
)

def execute_mcp_tool(tool_name: str, arguments: dict = None):
    arguments = arguments or {}
    try:
        if tool_name == "read_coding_guidelines": return read_coding_guidelines()
        elif tool_name == "get_repo_structure": return get_repo_structure()
        elif tool_name == "get_files": return get_files(arguments.get("file_paths", []))
        elif tool_name == "apply_edits": return apply_edits(arguments.get("edits", []))
        elif tool_name == "run_test_suite": return run_test_suite()
        elif tool_name == "get_repository_diff": return get_repository_diff()
        elif tool_name == "fetch_github_issue": return fetch_github_issue(arguments.get("issue_number"))
        elif tool_name == "publish_pull_request": return publish_pull_request(arguments.get("issue_number"), arguments.get("summary"))
        else: return f"Error: Tool '{tool_name}' not found."
    except Exception as e:
        return f"MCP Tool Execution Failed: {str(e)}"