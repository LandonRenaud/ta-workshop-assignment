from tools.mcp_client import execute_mcp_tool
from agents.single_agent import run_single_agent
from agents.planner import create_plan
from agents.developer import implement_feature
from agents.reviewer import review_feature

def run_single_agent_pipeline(issue_number: int):
    run_single_agent(issue_number)

def run_multi_agent_pipeline(issue_number: int, max_attempts: int = 4):
    print(f"--- Running Multi-Agent Pipeline for Issue #{issue_number} ---")

    issue = execute_mcp_tool("fetch_github_issue", {"issue_number": issue_number})
    repo = execute_mcp_tool("get_repo_structure")
    memory_context = execute_mcp_tool("read_coding_guidelines")

    plan = create_plan(issue, repo)
    files_needed = plan.get("files_to_modify", [])

    dev_feedback = None
    test_output = None
    accumulated_summaries = []

    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Attempt {attempt} of {max_attempts} ---")

        files_content = execute_mcp_tool("get_files", {"file_paths": files_needed})
        implementation = implement_feature(issue, plan, files_content, memory_context, dev_feedback, test_output)

        if "summary" in implementation:
            accumulated_summaries.append(f"- **Attempt {attempt}:** {implementation['summary']}")

        if "edits" in implementation:
            execute_mcp_tool("apply_edits", {"edits": implementation["edits"]})

        tests = execute_mcp_tool("run_test_suite")
        test_output = tests["output"]
        print(f"Test Status: {'PASSED' if tests['passed'] else 'FAILED'}")

        diff = execute_mcp_tool("get_repository_diff")
        review = review_feature(issue, plan, diff, tests, memory_context)
        status = review.get("status")
        dev_feedback = review.get("feedback")

        print(f"Review Status: {status}\nFeedback: {dev_feedback}")

        if tests["passed"] and status == "APPROVE":
            print("\nPipeline successful! Creating Pull Request...")

            full_summary = "\n".join(accumulated_summaries)

            pr_result = execute_mcp_tool("publish_pull_request", {
                "issue_number": issue_number,
                "summary": full_summary
            })

            print(f"Pull Request Status: {pr_result}")
            return

    print(f"\nPipeline failed after {max_attempts} attempts.")
