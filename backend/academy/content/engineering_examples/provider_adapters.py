"""Opt-in async external adapters. No call is made merely by importing this file.
Choose endpoints/models explicitly and run only with authorized synthetic data.
"""
import asyncio
import json
import os

async def ollama_stream(messages,endpoint='http://127.0.0.1:11434',model=None):
    import httpx
    model=model or os.environ['LOCAL_MODEL']
    payload={'model':model,'messages':messages,'stream':True}
    completed=False
    async with asyncio.timeout(60):
        async with httpx.AsyncClient(timeout=httpx.Timeout(30,connect=5)) as client:
            async with client.stream('POST',endpoint.rstrip('/')+'/api/chat',json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:continue
                    item=json.loads(line)
                    if 'error' in item:raise RuntimeError('local model error')
                    if item.get('message',{}).get('content'):
                        yield {'event':'draft_delta','text':item['message']['content']}
                    if item.get('done'):
                        completed=True
                        yield {'event':'draft_complete','input_tokens':item.get('prompt_eval_count'),
                               'output_tokens':item.get('eval_count'),'model':model}
    if not completed:raise RuntimeError('stream ended before completion; do not cache as a full answer')

async def cohere_rerank(query,candidates):
    import cohere
    if not query.strip() or not 1<=len(candidates)<=30:raise ValueError('query and 1–30 candidates required')
    client=cohere.AsyncClientV2(api_key=os.environ['COHERE_API_KEY'])
    async with asyncio.timeout(15):
        result=await client.rerank(model=os.environ['COHERE_RERANK_MODEL'],query=query,
                                  documents=[c['text'] for c in candidates],top_n=min(5,len(candidates)))
    ids=[]
    for row in result.results:
        if type(row.index) is not int or not 0<=row.index<len(candidates):raise ValueError('invalid rerank index')
        identifier=candidates[row.index]['id']
        if identifier in ids:raise ValueError('duplicate rerank result')
        ids.append(identifier)
    return ids

async def main():
    async for event in ollama_stream([{'role':'user','content':'Explain why a draft needs review in one sentence.'}]):
        print(json.dumps(event))
if __name__=='__main__':asyncio.run(main())
