import asyncio
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.retrieval import retrieve
from app.providers import FakeGenerator
from app.service import answer_question

client = TestClient(app)
documents = json.loads((Path(__file__).parent.parent / "data/policies.json").read_text())

def test_health_has_no_provider_dependency():
    assert client.get("/health").json()["mode"] == "lexical_fake_baseline"

def test_answer_contains_known_evidence():
    result = client.post("/ask", json={"question":"refund policy"})
    assert result.status_code == 200
    assert result.json()["citations"][0] == "refunds-1"
    assert set(result.json()["citations"]) <= {d["id"] for d in documents}
    assert "30 days" in result.json()["answer"]

def test_unrelated_terms_abstain():
    result = client.post("/ask", json={"question":"xyzzy quux"}).json()
    assert result["insufficient_evidence"] is True
    assert result["citations"] == []

def test_invalid_requests_are_rejected():
    assert client.post("/ask", json={"question":""}).status_code == 422
    assert client.post("/ask", json={"question":"refunds", "organization_id":"untrusted"}).status_code == 422

def test_document_filter_changes_available_evidence():
    result = client.post("/ask", json={"question":"refunds", "document_ids":["shipping-1"]}).json()
    assert result["insufficient_evidence"] is True

def test_unknown_document_is_not_silently_ignored():
    assert client.post("/ask", json={"question":"refunds", "document_ids":["missing"]}).status_code == 404

def test_retrieval_is_deterministic_and_bounded():
    assert retrieve("refunds shipping", documents, 1) == retrieve("refunds shipping", documents, 1)
    with pytest.raises(ValueError): retrieve("refund", documents, 0)

def test_unknown_generated_citation_is_rejected():
    class InvalidGenerator:
        async def generate(self, question, passages):
            return {"answer":"Invented", "citations":["not-retrieved"]}
    with pytest.raises(ValueError, match="Unknown citation"):
        asyncio.run(answer_question("refund policy", documents, InvalidGenerator()))
