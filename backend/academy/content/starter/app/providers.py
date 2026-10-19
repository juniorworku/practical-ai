"""Offline fake: quotes retrieved text. No SDK, key, network, or invented facts."""
class FakeGenerator:
    async def generate(self, question, passages):
        return {"answer": " ".join(p["text"] for p in passages),
                "citations": [p["id"] for p in passages],
                "insufficient_evidence": False,
                "mode": "lexical_fake_baseline"}
