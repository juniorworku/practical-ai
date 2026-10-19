"""Local baseline only. Add auth, persistence and real retrieval in the daily labs."""
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from .schemas import AskRequest, Answer
from .providers import FakeGenerator
from .service import answer_question

app = FastAPI(title="GenAI Accelerator Capstone — local baseline")
FIXTURE = Path(__file__).resolve().parent.parent / "data" / "policies.json"

@app.get("/health")
def health():
    return {"status": "ok", "mode": "lexical_fake_baseline"}

@app.post("/ask", response_model=Answer)
async def ask(body: AskRequest):
    documents = json.loads(FIXTURE.read_text())
    if body.document_ids:
        available = {d["id"] for d in documents}
        if not set(body.document_ids) <= available:
            raise HTTPException(status_code=404, detail="Fixture document not found")
        documents = [d for d in documents if d["id"] in body.document_ids]
    return await answer_question(body.question, documents, FakeGenerator())
