"""Inspectable lexical baseline. This is NOT semantic retrieval."""
import re

def terms(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def retrieve(question, documents, limit=3):
    if not 1 <= limit <= 10:
        raise ValueError("limit must be 1..10")
    query = terms(question)
    ranked = [(len(query & terms(d["text"])), d) for d in documents]
    ranked = sorted(ranked, key=lambda pair: (-pair[0], pair[1]["id"]))
    return [document for score, document in ranked[:limit] if score > 0]
