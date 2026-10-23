import asyncio
from dataclasses import dataclass
from typing import Protocol

class ProviderError(RuntimeError): pass

@dataclass(frozen=True)
class Reply:
    text: str
    source: str | None
    input_tokens: int | None
    output_tokens: int | None

class Provider(Protocol):
    async def answer(self, query: str, evidence: dict) -> Reply: ...

def validate(reply, source):
    if not isinstance(reply, Reply) or reply.source != source:
        raise ProviderError('Invalid result type or source')
    if not isinstance(reply.text, str) or not reply.text.strip() or len(reply.text) > 8000:
        raise ProviderError('Invalid answer text')
    for count in (reply.input_tokens, reply.output_tokens):
        if count is not None and (type(count) is not int or count < 0):
            raise ProviderError('Invalid usage')
    return reply

class Fake:
    async def answer(self, query, evidence):
        return Reply('14 days', evidence['id'], None, None)

async def application(provider: Provider):
    evidence = {'id':'policy-v1','text':'Unused returns within 14 days.'}
    async with asyncio.timeout(1):
        reply = await provider.answer('refund window?', evidence)
    return validate(reply, evidence['id'])

reply = asyncio.run(application(Fake()))
assert reply.input_tokens is None and reply.output_tokens is None
print('Validated reply; absent usage remains unknown:', reply)
# Runtime validation raises explicit errors; assertions below test outcomes only.
