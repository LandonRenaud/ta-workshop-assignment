# TA Workshop: Single Agent and Multi-Agent Feature Development

This starter is a small Flask task tracker. The exercise adds Low, Medium,
and High priority, defaults missing priority to Medium, and displays it in
the frontend. The starter intentionally does not implement priority yet.

## Local setup

Use Python 3.10 or newer. Clone the course repository, then run:

```bash
git clone https://github.gatech.edu/CS-3300-Intro-to-Software-Eng/ta-workshop-starter.git
cd ta-workshop-starter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest tests -q
python app.py
```

On Windows, activate with `.venv\Scripts\activate`. Open
`http://127.0.0.1:5000` to inspect the starter, then stop the app with Ctrl+C.

For TA maintenance, run `python -m pytest tools/test_mcp.py -q` separately.
These tooling checks are not part of the app's feature test suite.

To run an agent flow, set `OPENAI_API_KEY` privately in your terminal using
your course access, then run `python main.py` and choose 1 or 2. Do not put
keys in source files, chat, screenshots, or commits. Local execution uses a
fixed practice issue and mocks PR creation; it does not push a branch.

## What to follow during the demo

- **Single:** loads all exposed app/test files, makes one implementation
  call, runs pytest, and has no automatic repair loop or separate Reviewer.
- **Multi:** the Planner sees file names first; the Developer loads selected
  files; pytest and git diff go to the Reviewer with the original issue.
  Passing tests AND an APPROVE decision are required before publication.
- A REQUEST_MORE_TESTS decision adds `tests/test_app.py` to the next
  Developer context. Test output and review feedback guide bounded retries.
  The Reviewer is asked to check for new tests; approval is not proof that
  the feature is correct.
- These are differences between these two example workflows, not a claim
  that every multi-agent system is better than every single-agent system.

## Tool transport and demo boundary

`tools/mcp_client.py` starts `tools.mcp_server` as a subprocess, initializes
an MCP stdio session, and calls its tools. stdout is reserved for MCP traffic.
The server exposes only app/test paths for agent reads and edits.

No Docker is required. pytest runs as a subprocess on the current machine
or GitHub runner, without the model/GitHub tokens in its environment.
This is not a security sandbox: run only the TA-controlled exercise in a
disposable checkout/runner, not arbitrary issues, forks, or untrusted code.

On Actions, a TA adds `approved` to the trusted issue to start the existing
workflow. Successful runs create a PR for human review; nothing auto-merges.
Local checks do not verify runner availability or live PR publication.
