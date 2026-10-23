"""Small, executable supplements; never execute student Python in Django."""
import hashlib
import json

LABS = {
 '01': {
  'title': 'Enforce the read-only task boundary',
  'teaching': '''A scope statement needs an application guard. In this small offline lab, `route_request(kind)` receives a normalized request label and returns the permitted route. The label is synthetic input, not a model decision or a real intent classifier.

1. Write a function with `def route_request(kind):`. Python passes the caller's value into `kind`.
2. Use `if kind == "policy_question":` to select the one supported request. Return `"draft"` for that value.
3. For `"refund"`, return `"human_review"`. This routes an action request; it does not approve or execute a refund.
4. Every other value must return `"out_of_scope"`. Do not default unknown requests to an action.
5. Run the checks, then deliberately change the unknown fallback to `"draft"` and observe the failing case. Restore the safe boundary.

Example: `route_request("policy_question")` should equal `"draft"`. The other cases below are the contract you must implement. A few string comparisons are fast and free of model costs; their quality is limited to enforcing these explicit labels. They do not understand natural language. Context is only the request kind, with no conversation history.''',
  'starter': 'def route_request(kind):\n    # Implement the three routes described above.\n    raise NotImplementedError("Implement the scope guard")\n',
  'solution': 'def route_request(kind):\n    if kind == "policy_question":\n        return "draft"\n    if kind == "refund":\n        return "human_review"\n    return "out_of_scope"\n',
  'checks': [
   ('Policy question stays read-only', 'route_request("policy_question") == "draft"', 'Return draft for the supported policy question; never execute an action.'),
   ('Refund requires human review', 'route_request("refund") == "human_review"', 'The release excludes refunds. Route the request to a person.'),
   ('Unknown label fails closed', 'route_request("delete_account") == "out_of_scope"', 'Unknown requests must not inherit permission from the happy path.'),
   ('Missing label fails closed', 'route_request(None) == "out_of_scope"', 'Only explicit supported labels have a route. Missing input grants no authority.'),
  ],
 },
 '03': {
  'title': 'Score an evaluation set without hiding failures',
  'teaching': '''Build the simplest repeatable behavioral scorer before adding an LLM judge. Each synthetic row is a dictionary with `expected` and `actual` behavior labels: answer, clarify or abstain. This lab scores label agreement only; it cannot establish whether answer text is factually supported.

1. Define `score_cases(rows)` and create an integer counter `correct = 0`.
2. Loop with `for row in rows:`. Compare `row["actual"] == row["expected"]` and increment only for a match.
3. Return `{"correct": correct, "total": len(rows)}`. Always include failures in the denominator.
4. An empty list returns zero correct out of zero. Do not divide by zero or report perfect quality for no evidence.
5. Keep development and holdout labels outside this function. The scorer must not silently discard hard cases.

Worked example: for `[{"expected": "abstain", "actual": "answer"}]`, the result is `{"correct": 0, "total": 1}`. Try changing actual to abstain and predict the new count before running it. This linear pass is cheap and deterministic; add separately reviewed factual-support labels for semantic quality. The scorer reads only the supplied cases, with no accumulating chat context.''',
  'starter': 'def score_cases(rows):\n    # Count every case; keep the correct count separate from total.\n    raise NotImplementedError("Implement the behavioral scorer")\n',
  'solution': 'def score_cases(rows):\n    correct = 0\n    for row in rows:\n        if row["actual"] == row["expected"]:\n            correct += 1\n    return {"correct": correct, "total": len(rows)}\n',
  'checks': [
   ('Empty is not perfect evidence', 'score_cases([]) == {"correct": 0, "total": 0}', 'Return both zero counts without dividing.'),
   ('Correct abstention is a success', 'score_cases([{"expected":"abstain","actual":"abstain"}]) == {"correct":1,"total":1}', 'Quality includes refusing unsupported questions, not just producing answers.'),
   ('Unsupported answers remain failures', 'score_cases([{"expected":"abstain","actual":"answer"}]) == {"correct":0,"total":1}', 'Do not drop an incorrect case from total.'),
   ('Mixed results keep the denominator', 'score_cases([{"expected":"answer","actual":"answer"},{"expected":"clarify","actual":"answer"},{"expected":"abstain","actual":"abstain"}]) == {"correct":2,"total":3}', 'Count two label matches across all three cases.'),
  ],
 },
 '04': {
  'title': 'Validate an answer contract before using it',
  'teaching': '''Implement `valid_result(result, allowed_ids)` returning a boolean. The caller already parsed JSON into Python values; your job is structural and citation-identity checking, not factual judgment.

1. Require a dictionary with exactly the keys status, answer and citations. `set(result)` gives dictionary keys; compare it with a set literal.
2. Require status to be answer or abstain, answer to be a string, citations to be a list of strings. Use `isinstance(value, str)` and `all(...)` for each list item.
3. Reject duplicate citations using `len(set(citations)) != len(citations)`. Only do this after checking every item is a string.
4. Every citation must occur in `allowed_ids`; `all(c in allowed_ids for c in citations)` checks membership.
5. An answer must contain non-whitespace text and at least one citation. Abstention must have an empty answer and no citations.

A complete branch example is `if not isinstance(result, dict): return False`. Apply this pattern before reading keys. For `{"status":"answer","answer":"14 days","citations":["returns-v1"]}` and allowed_ids `["returns-v1"]`, the result is True. A made-up citation must return False. A false policy claim with a real ID can still pass: inspect passage support separately. These small deterministic checks add little latency or cost and restrict citations to the selected evidence context.''',
  'starter': 'def valid_result(result, allowed_ids):\n    # Validate types before sets or dictionary access.\n    raise NotImplementedError("Implement the response contract")\n',
  'solution': '''def valid_result(result, allowed_ids):
    if not isinstance(result, dict) or set(result) != {"status", "answer", "citations"}:
        return False
    status, answer, citations = result["status"], result["answer"], result["citations"]
    if status not in ("answer", "abstain") or not isinstance(answer, str):
        return False
    if not isinstance(citations, list) or not all(isinstance(c, str) for c in citations):
        return False
    if len(citations) != len(set(citations)) or not all(c in allowed_ids for c in citations):
        return False
    if status == "answer":
        return bool(answer.strip()) and bool(citations)
    return answer == "" and citations == []
''',
  'checks': [
   ('Supported shape', 'valid_result({"status":"answer","answer":"14 days","citations":["r1"]}, ["r1"]) is True', 'A nonempty answer with a selected citation has the required structure.'),
   ('Abstention shape', 'valid_result({"status":"abstain","answer":"","citations":[]}, []) is True', 'Abstention does not manufacture an answer or a citation.'),
   ('Made-up citation', 'valid_result({"status":"answer","answer":"14 days","citations":["fake"]}, ["r1"]) is False', 'A citation must come from the selected evidence set.'),
   ('Duplicate citation', 'valid_result({"status":"answer","answer":"14 days","citations":["r1","r1"]}, ["r1"]) is False', 'Duplicate IDs do not add evidence; reject them.'),
   ('Malformed input', 'all(valid_result(value, []) is False for value in [None, [], {}, {"status":"answer","answer":7,"citations":[]}])', 'Check the container, exact keys and field types before accessing values.'),
   ('Unhashable citation', 'valid_result({"status":"answer","answer":"x","citations":[{}]}, ["r1"]) is False', 'Check citation types before constructing a set.'),
   ('Empty answer and uncited answer', 'all(valid_result({"status":"answer","answer":text,"citations":ids}, ["r1"]) is False for text, ids in [(" ",["r1"]),("x",[])])', 'Answers need meaningful text and at least one selected citation.'),
   ('Extra fields rejected', 'valid_result({"status":"abstain","answer":"","citations":[],"execute":True}, []) is False', 'Do not accept undeclared action fields.'),
  ],
 },
}

def lesson_lab(lesson):
    if lesson.program.slug != 'ai-agent-bootcamp':
        return None
    spec = LABS.get(lesson.source_id.rsplit(':', 1)[-1])
    if not spec:
        return None
    lab = {**spec, 'checks': [{'name': n, 'expression': e, 'feedback': f} for n, e, f in spec['checks']]}
    lab['revision'] = hashlib.sha256(json.dumps(lab, sort_keys=True).encode()).hexdigest()
    return lab
