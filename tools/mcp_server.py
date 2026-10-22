import os
import subprocess
import json
import urllib.request
from urllib.error import HTTPError
import textwrap
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("WorkshopTools")

@mcp.tool()
def read_coding_guidelines() -> str:
    try:
        with open("docs/coding_guidelines.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Warning: Coding guidelines document not found."

@mcp.tool()
def get_repo_structure() -> str:
    structure = []
    for root, dirs, files in os.walk("."):
        if any(ignore in root for ignore in ['.git', '__pycache__', 'venv', '.pytest_cache']):
            continue
        for file in files:
            if file.endswith(('.py', '.html', '.js', '.css', '.txt')):
                structure.append(os.path.join(root, file))
    return "\n".join(structure)

@mcp.tool()
def get_files(file_paths: list[str]) -> str:
    contents = []
    for path in file_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                contents.append(f"--- FILE: {path} ---\n{f.read()}\n")
        else:
            contents.append(f"--- FILE: {path} ---\n(File does not exist)\n")
    return "\n".join(contents)

@mcp.tool()
def apply_edits(edits: list[dict]) -> str:
    for edit in edits:
        file_path = edit.get("file_path")
        content = edit.get("content")
        if file_path and content:
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
    return f"Successfully applied {len(edits)} edits."

@mcp.tool()
def run_test_suite() -> dict:
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v"], 
            capture_output=True, text=True, timeout=30
        )
        return {"passed": result.returncode == 0, "output": result.stdout + "\n" + result.stderr}
    except Exception as e:
        return {"passed": False, "output": f"Test execution failed: {str(e)}"}

@mcp.tool()
def get_repository_diff() -> str:
    try:
        result = subprocess.run(["git", "diff"], capture_output=True, text=True)
        return result.stdout
    except Exception:
        return "Could not retrieve git diff."

@mcp.tool()
def fetch_github_issue(issue_number: int) -> str:
    if not os.getenv("GITHUB_ACTIONS"):
        return textwrap.dedent("""\
            Title: Add task priority
            Body: 
            - Tasks can be Low, Medium, or High priority.
            - The user can choose priority when creating a task.
            - The backend stores and returns the priority.
            - The frontend displays the priority.
            - Missing priority defaults to Medium.
            - Existing behavior should continue working.
        """)
        
    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")
    if not repo or not token or not issue_number:
        return "Error: Missing GitHub Action environment variables."
        
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TA-Workshop-Demo-Agent"
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return f"Title: {data.get('title')}\nBody: {data.get('body')}"
    except HTTPError as e:
        error_body = e.read().decode()
        return f"GitHub API Error {e.code}: {error_body}"
    except Exception as e:
        return f"Failed to fetch issue: {str(e)}"

@mcp.tool()
def publish_pull_request(issue_number: int, summary: str) -> str:
    if not os.getenv("GITHUB_ACTIONS"):
        print(f"\n[LOCAL MOCK PR] Creating PR for Issue #{issue_number}\nSummary: {summary}\n")
        return "PR creation mocked locally."
    
    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")
    branch_name = f"feature-issue-{issue_number}"

    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        subprocess.run(["git", "add", "."], check=True)

        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            return "No file changes detected; aborted pull request creation."

        subprocess.run(["git", "commit", "-m", f"Implement feature for issue #{issue_number}"], check=True)
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

        api_base = os.getenv("GITHUB_API_URL", "https://api.github.com")
        url = f"{api_base}/repos/{repo}/pulls"
        data = json.dumps({
            "title": f"Automated Feature Implementation (Issue #{issue_number})",
            "body": f"Resolves #{issue_number}.\n\n### Summary of Changes:\n{summary}",
            "head": branch_name,
            "base": "main"
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "TA-Workshop-Demo-Agent"
        }, method="POST")

        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            return f"Successfully created PR: {res_data.get('html_url')}"

    except subprocess.CalledProcessError as e:
        return f"Git operation failed: {e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)}"
    except HTTPError as e:
        error_body = e.read().decode()
        return f"GitHub API Error {e.code}: {error_body}"
    except Exception as e:
        return f"Failed to create PR: {str(e)}"

if __name__ == "__main__":
    mcp.run()