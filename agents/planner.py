from tools.llm import call_llm_json

def create_plan(issue: str, repo_structure: str) -> dict:
    prompt = f"""
    You are a Software Architect.

    Issue Requirement: {issue}

    Repository Structure: {repo_structure}

    Create an implementation plan. Return a JSON object with:
    1. "files_to_modify": List of file paths that need changing. Do NOT include test files here.
    2. "plan": Step-by-step instructions for the developer. Do NOT include instructions to write tests for this initial feature build.
    """
    print("Planner is creating the architectural design...")
    return call_llm_json(prompt)