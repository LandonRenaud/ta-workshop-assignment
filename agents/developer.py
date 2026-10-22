from tools.llm import call_llm_json

def implement_feature(issue: str, plan: dict, file_contents: str, memory_context: str, feedback: str = None, test_output: str = None) -> dict:
    prompt = f"""
    You are an Expert Developer.

    Issue Requirement: {issue}

    Implementation Plan: {plan.get('plan')}

    Current File Contents: {file_contents}

    Coding Guidelines: {memory_context}
    """

    if feedback:
        prompt += f"""
        PREVIOUS ATTEMPT FAILED. 

        Test Results: {test_output}

        Reviewer Feedback: {feedback}

        Fix the implementation or add tests to tests/test_app.py based on reviewer feedback and test output.
        """

    prompt += """
    Write the code required to implement the feature strictly adhering to coding guidelines and existing code structure. Return a JSON object with:
    1. "edits": A list of objects containing "file_path" and "content" (providing the fully updated file content, not just a diff).
    2. "summary": A brief description of the code changes.
    """
    print("Developer is writing/updating the code...")
    return call_llm_json(prompt)