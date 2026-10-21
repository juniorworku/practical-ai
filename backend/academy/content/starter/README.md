# GenAI Accelerator capstone starter

This is a local lexical/fake baseline, not a production application or a semantic RAG system. It requires no API key or GPU. The reviewed lessons teach scoped access, persistent storage, background ingestion, retrieval, evaluation and deployment. The separate `accelerator_stack/` case study contains the complete local API/PostgreSQL/worker service. Keep it separate from Resume Studio.

1. Extract the course ZIP and open `workspace/` (the folder containing pyproject.toml) in VS Code.
2. Install uv from its official documentation if necessary. Use Python 3.12.
3. In this folder run `uv sync --extra dev`. The provided `uv.lock` was resolved and tested for this starter. Use `uv sync --locked --extra dev` to reproduce it; update the lock deliberately when adding lab dependencies.
4. Run `uv run pytest` and `uv run python -m evals.run_baseline`.
5. Start the local API with `uv run uvicorn app.main:app --reload --port 8010` and open `http://127.0.0.1:8010/docs`.
6. Work through the app's Day 1 lab. Save commands, results, and changed files as evidence.

Fixtures are fictional policies. The fake generator quotes retrieved passages; it does not demonstrate real LLM inference. Lexical matching has deliberate weaknesses, including common-word matches and synonym failures. The unknown baseline question can retrieve irrelevant candidates; keep that failure in your report and improve it in the retrieval labs.

Do not expose this initial API publicly: it has no authentication, persistence, queues, or real provider adapter yet. Do not use Resume Studio's database, credentials, or volumes for these experiments. New dependencies and real service calls are learner-controlled decisions described in the lessons.

## Suggested artifacts as you progress

`docs/product-brief.md`, `docs/architecture.md`, `docs/decisions.md`, `evals/answers.jsonl`, `evals/retrieval.jsonl`, `docs/release-assessment.md`. Record known gaps rather than filling reports with assumed successful results.

## Advanced agent path

`agent_lab.py` is a scripted, standard-library loop baseline. Run `python -m unittest discover -s tests -p test_agent_lab.py -v` from this folder. It demonstrates bounded steps, rejected calls and explicit stop reasons; it does not verify answer truth or implement MCP, checkpoints or multi-agent orchestration. Lessons 61–84 and labs 15–20 guide you to implement those separately. MCP exercises require a matching official SDK server/client and their own environment; no new SDK is installed in Workshop.

### Complete runnable walkthroughs

Open `advanced/README.md` for step-by-step agent, LangGraph and MCP server/client builds. This folder uses its own virtual environment and pinned SDKs; start at Accelerator lesson 61, 68 or 80.
