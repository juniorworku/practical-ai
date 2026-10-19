from pydantic import BaseModel, ConfigDict, Field

class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=3, max_length=2000)
    document_ids: list[str] = Field(default_factory=list, max_length=20)

class Answer(BaseModel):
    answer: str = Field(max_length=6000)
    citations: list[str] = Field(default_factory=list, max_length=10)
    insufficient_evidence: bool = False
    mode: str = "lexical_fake_baseline"
