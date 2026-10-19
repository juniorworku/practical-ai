# Runnable advanced exercises

Work in this folder after extracting the course ZIP. Use Python 3.12 on your Intel Mac.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python agent.py
python graph.py
python -m unittest test_examples -v
python mcp_client.py
```

Read agent-walkthrough.md, graph-walkthrough.md and mcp-walkthrough.md in order. They include complete files, explanations, expected output, failure experiments and limitations. The agent uses a scripted decision adapter; the graph uses real LangGraph and in-memory checkpoints; the MCP test launches a real local SDK subprocess. No model API calls or GPU are needed. No Workshop database access occurs. Top-level SDK versions are pinned; transitive versions used in validation are recorded in tested-environment.txt. No production-readiness claim is implied.

## Real model connection

Lesson 85 and `live-provider-walkthrough.md` connect the agent to Workshop’s existing provider settings through the installed `practice_agent` command. Scripted runs remain the default; `--live` enables API requests. No credentials are included in this download. `model_adapter.py` also accepts a fake request for offline tests.
