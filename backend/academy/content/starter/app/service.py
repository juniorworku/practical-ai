from .schemas import Answer
from .retrieval import retrieve

async def answer_question(question, documents, generator):
    passages = retrieve(question, documents)
    if not passages:
        return Answer(answer="I do not have enough evidence to answer.", insufficient_evidence=True)
    answer = Answer.model_validate(await generator.generate(question, passages))
    if not set(answer.citations) <= {p["id"] for p in passages}:
        raise ValueError("Unknown citation")
    return answer
