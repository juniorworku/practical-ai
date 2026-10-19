# Practical programs: offline lab workspace

These exercises run locally in a **separate folder**, not inside the academy server. They require Python 3.12+ and its standard library. No model credentials, network access, or paid calls are needed. They are small teaching baselines, not production AI implementations.

## Run the exercises

1. Extract the learning kit and open `program_labs` as your project folder.
2. Read the functions in `exercises.py` and implement one at a time.
3. Run `python3 -m unittest discover -s tests -v` (or your Windows Python command). The initial exercises intentionally raise `NotImplementedError`; failing tests are expected before implementation.
4. To check the supplied reference implementation, run `LAB_MODULE=reference python3 -m unittest discover -s tests -v` on macOS/Linux. On PowerShell: `$env:LAB_MODULE='reference'; python -m unittest discover -s tests -v`.
5. Compare behavior on a new input you design, then save your own observed output and explanation. Reading a reference implementation is not evidence that you ran it.

## Six concrete labs

| Lab | Implement | What to investigate |
|---|---|---|
| Retrieval | `retrieve(query, passages, k)` | Lexical term overlap, deterministic ties, missing evidence, source identity |
| Extraction | `validate_record(record)` | Unknown fields, decimal arithmetic, invalid types, mismatched totals |
| Citations | `validate_citations(answer, citations, available)` | Unsupported IDs, empty evidence, what validation cannot establish about meaning |
| Bounded agent | `run_agent(decide, max_steps)` | Stop conditions, repeated tool requests, unknown actions, failed observations |
| Routing | `routing_metrics(expected, predicted)` | Confusion matrices, per-label support, rare-class failures |
| Economics | `net_minutes(volume, manual, assisted, review, exceptions, exception_minutes)` | Net benefit after review and exception work, invalid assumptions |

`fixtures.json` contains synthetic policies, extraction examples, and routing examples. Expand it for your course projects. `templates/` contains editable client-delivery and evaluation worksheets. The reference code does not call a model, perform semantic retrieval, authorize real users, send messages, or execute external actions. Extend it only after defining and testing those boundaries.
