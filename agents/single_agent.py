from tools.llm import call_llm_json
from tools.mcp_client import execute_mcp_tool


def run_single_agent(issue_number: int):
    print(f"--- Running Single Agent for Issue #{issue_number} ---")

    issue = execute_mcp_tool("fetch_github_issue", {"issue_number": issue_number})
    repo_structure_str = execute_mcp_tool("get_repo_structure")

    repo_paths = [p.strip() for p in repo_structure_str.split("\n") if p.strip()]

    files_content = execute_mcp_tool("get_files", {"file_paths": repo_paths})

    memory_context = execute_mcp_tool("read_coding_guidelines")

    prompt = f"""
    You are an autonomous software engineer.

    Issue Requirement: {issue}

    Current File Contents: {files_content}

    Coding Guidelines: {memory_context}

    Write the code required to implement the feature strictly adhering to coding guidelines and existing code structure. Return a JSON object with:
    1. "edits": A list of objects containing "file_path" and "content" (providing the fully updated file content, not just a diff).
    2. "summary": A brief description of the code changes.
    """

    print("Agent is implementing the issue feature...")
    result = call_llm_json(prompt)

    if "edits" in result:
        execute_mcp_tool("apply_edits", {"edits": result["edits"]})
    else:
        print("Agent failed to return 'edits' array.")
        return

    tests = execute_mcp_tool("run_test_suite")
    print(f"Test Status: {'PASSED' if tests['passed'] else 'FAILED'}")
    print(tests['output'])

    if tests["passed"]:
        print("\nTests passed! Creating Pull Request...")
        pr_result = execute_mcp_tool("publish_pull_request", {
            "issue_number": issue_number,
            "summary": result.get("summary", "Automated feature implementation")
        })
        print(f"Pull Request Status: {pr_result}")
