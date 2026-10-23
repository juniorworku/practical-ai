from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Request:
    owner: str
    query: str
    def __post_init__(self):
        if not isinstance(self.query, str) or not self.query.strip() or len(self.query) > 2000:
            raise ValueError('query must contain 1–2000 characters')

class Provider(Protocol):
    async def answer(self, request: Request) -> str: ...

request = Request('team-a', 'refund window')
assert request.query == 'refund window'
try:
    Request('team-a', '')
except ValueError:
    print('Invalid input rejected before provider work')
else:
    raise AssertionError('empty query accepted')
# frozen=True prevents reassignment; it does not recursively freeze mutable fields.
print('Contract accepted:', request.owner)
