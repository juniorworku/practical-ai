import asyncio
from dataclasses import dataclass

class ProviderError(RuntimeError):pass
@dataclass(frozen=True)
class Reply:
    text:str
    source:str
    input_tokens:int|None=None

def validate(value):
    if not isinstance(value,Reply):raise ProviderError('shape')
    if not isinstance(value.text,str) or not value.text.strip():raise ProviderError('empty text')
    if value.source!='p1':raise ProviderError('source')
    if value.input_tokens is not None and (type(value.input_tokens) is not int or value.input_tokens<0):raise ProviderError('usage')
    return value

for value in [None,Reply('','p1'),Reply('answer','other'),Reply('answer','p1',True),Reply('answer','p1',-1)]:
    try:validate(value)
    except ProviderError:pass
    else:raise AssertionError('invalid response accepted')
assert validate(Reply('answer','p1')).input_tokens is None
assert validate(Reply('answer','p1',9)).input_tokens==9
print('Response shape, text, source and usage matrix passed without a live model')
