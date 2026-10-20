# Software-first academy and the independent AI Engineering program

All four authored practical programs have their own teaching, examples, practice and progress. The GenAI Accelerator remains independent. Enrollment is free; optional provider, cloud and GPU experiments require a learner's own authorized accounts and can incur charges.

The new AI Engineering path contains 36 build sessions, roughly 149 estimated practice hours over twelve weeks. It expects Python, HTTP/JSON, SQL and Git basics. The estimate includes implementation and review; it is not timed video duration or a guarantee of proficiency.

| Weeks | Module | Capstone and release evidence |
|---|---|---|
| 1–2 | Modern AI stack and foundational APIs | Bidirectional voice gateway; PCM capture/playback, bounded async work, cancellation/interruption, token/usage accounting and measured live latency |
| 3–5 | Data grounding and advanced RAG | PDF/DOCX/approved-site/VTT ingestion, provenance, versioned vectors, scoped search, hybrid fusion, reranking and grounded streaming with no-answer evaluation |
| 6–8 | Agentic workflows and multi-agent systems | Workspace monitor/draft/calendar proposal, durable inbox/checkpoints, exact approval, reconciliation and MCP; framework/delegation compared against a fixed workflow |
| 9–10 | LLMOps, evaluation and observability | 120 concrete contract inputs across twelve families and ten tenant variants; CI/release manifests, critical gates, minimized traces, semantic calibration and useful-output economics |
| 11–12 | Scaling, hosting and edge deployment | Container/PostgreSQL recovery, Cloud Run deployment experiment/ECS comparison, Ollama adapter/vLLM serving decisions, GPU/context budgeting, quotas and an evidence-backed hybrid SaaS handover |

Each session teaches three concepts step by step before implementation, traces the complete executable standard-library baseline, and then sets a bounded practice task before the larger integration project. Three progressive hints, a complete inline reference solution with expected observations and failure diagnosis, reflection self-review guidance, choice-specific server-side quiz feedback, flashcards and a practical evidence rubric support the learner. Incorrect quiz answers link directly back to the concept teaching. Integration sessions include full files inline, setup instructions, limits and an explicit boundary between local evidence and live-provider evidence. No external repository or workbook is needed to read the teaching.

Every authored module finishes with four additional release gates: latency/cost/quality comparison; repeatable automated checks and separate factual review; context/cache/owner policy; and a bounded deployment/failure experiment. New learning revisions preserve previous attempts and submissions rather than treating changed rubrics as the same assignment. Imported Accelerator/Tutor/library readings receive the same engineering brief through the API and reader without overwriting their original source content.

The 3 pillars are applied to the module's actual work. For example, freelancing discovery inventories approved inputs and measures current reviewer effort; its scope module turns promises into Given/When/Then acceptance and usage allowances; its handover module requires restart/readback, isolated restore and cache-revocation ownership. They do not redirect to the Accelerator.

## Evaluation boundaries

The 120-case harness is a contract suite, not 120 independent tasks or a load benchmark. Tenant variants remain grouped with their scenario family. It sends actual prompts/state to an optional HTTP adapter without expected labels, retains failures and missing usage, and blocks on critical failures. The default deterministic rule fixture only validates the harness and mechanical behavior. It leaves semantic review at zero. Claim-level support, relevance and judge calibration require separately reviewed evidence; model judges are not deterministic ground truth.

Likewise, PCM echo is not speech reasoning, an in-memory LangGraph saver is not restart durability, the three-dimensional pgvector data is not semantic retrieval, a local fake effect is not remote exactly-once delivery, and configured cloud concurrency or illustrative GPU arithmetic is not measured production scale. These boundaries are part of the lessons and assessments.

## Research and provenance

The requested AI Engineering from Scratch repository was read as background topic coverage. Its source notice remains included in the generated learning content. The academy teaching and specimens are authored locally; there are no learner redirects to that repository. API implementation details were checked against primary documentation:

- [Gemini Live capabilities](https://ai.google.dev/gemini-api/docs/live-api/capabilities) — concurrent audio/text sessions, PCM formats, interruptions and turn handling.
- [Gemini token accounting](https://ai.google.dev/gemini-api/docs/tokens) — preflight counts versus completed usage.
- [pgvector](https://github.com/pgvector/pgvector) — cosine indexes, scoped queries and approximate-search filtering considerations.
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) — checkpoints, thread IDs, resumes and node re-execution.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — host/client/server capabilities and invocation boundaries.
- [Cohere rerank reference](https://docs.cohere.com/v2/reference/rerank) — candidate-index mapping and bounded reranking.
- [Ragas faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) — semantic claim/support judgments, distinguished from deterministic contracts.
- [Cloud Run WebSockets](https://docs.cloud.google.com/run/docs/triggering/websockets) — timeouts, reconnection and cross-instance state.
- [Ollama chat API](https://docs.ollama.com/api/chat) and [vLLM serving](https://docs.vllm.ai/en/latest/serving/openai_compatible_server/) — local streaming and transport compatibility boundaries.
- [Ollama embeddings](https://docs.ollama.com/api/embed) — batch input, explicit no-truncation requests, returned vectors and usage; the full adapter validates index compatibility before accepting output.
- [Gmail metadata retrieval](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get) and [draft creation](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.drafts/create) — separate OAuth requirements and a reviewed draft-only boundary.

## Student teaching review

See [the 36-lesson student review](engineering-student-review.md) for concrete teaching and example repairs, and the final verification evidence. The program can be studied entirely inside the lesson reader; the optional source archive supplements the inline teaching.
