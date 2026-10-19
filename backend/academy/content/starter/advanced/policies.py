"""Synthetic, allowlisted evidence. No files, network or user database access."""
POLICIES = {"policy-1": "Refund requests must be submitted within 30 days.",
            "policy-2": "Support is available Monday through Friday."}

def search(query: str) -> list[dict[str, str]]:
    if not isinstance(query, str) or not 3 <= len(query) <= 200:
        raise ValueError("query must contain 3..200 characters")
    words = set(query.lower().split())
    return [{"id": key, "text": text} for key, text in POLICIES.items()
            if words & set(text.lower().replace(".", "").split())]
