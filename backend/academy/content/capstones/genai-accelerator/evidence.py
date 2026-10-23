"""Conservative whole-document context for this small synthetic-policy capstone."""
def select_document(chunks, question, budget=1000):
    terms=set(question.lower().split())
    if not any(terms & set(chunk['text'].lower().split()) for chunk in chunks):
        return [],0
    # Sentence chunks may depend on one another. Retain the complete document
    # rather than dropping an unmatched exception from another sentence.
    used=sum(len(chunk['text']) for chunk in chunks)
    if used>budget:
        raise ValueError('context_review_required')
    return list(chunks),used
