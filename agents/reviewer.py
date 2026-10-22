from tools.llm import call_llm_json

def review_feature(issue: str, plan: dict, diff: str, test_results: dict, memory_context: str) -> dict:
    prompt = f"""
    You are a Senior Code Reviewer.

    Issue Requirement: {issue}

    Git Diff: {diff}

    Test Results: {'Passed' if test_results['passed'] else 'Failed'} - {test_results['output']}

    Coding Guidelines: {memory_context}

    Evaluate the changes. 
    - If tests fail or code doesn't follow guidelines, request changes.
    - If new feature logic was added but no new tests were added, request more tests.

    Return a JSON object with:
    1. "status": Strictly "APPROVE", "REQUEST_CHANGES", or "REQUEST_MORE_TESTS".
    2. "feedback": A brief explanation of your decision.
    """
    print("Reviewer is evaluating the implementation...")
    return call_llm_json(prompt)