"""Explicit opt-in local embedding adapter; install httpx and an embedding model.
Set LOCAL_EMBEDDING_MODEL and EXPECTED_EMBEDDING_DIMENSIONS after selecting and
inspecting your model. Importing performs no request. Never mix model indexes.
"""
import asyncio,math,os
import httpx
async def embed(texts,model,dimensions,endpoint='http://127.0.0.1:11434',transport=None):
    if not 1<=len(texts)<=32 or any(not isinstance(t,str) or not t.strip() or len(t)>20000 for t in texts):
        raise ValueError('1–32 nonempty bounded text chunks required')
    if not model or type(dimensions) is not int or dimensions<1:raise ValueError('model/index contract required')
    async with asyncio.timeout(30):
        async with httpx.AsyncClient(timeout=20,transport=transport) as client:
            response=await client.post(endpoint.rstrip('/')+'/api/embed',json={'model':model,'input':texts,'truncate':False})
            response.raise_for_status();data=response.json()
    vectors=data.get('embeddings')
    if data.get('model')!=model or not isinstance(vectors,list) or len(vectors)!=len(texts):raise ValueError('model or batch mismatch')
    for vector in vectors:
        if not isinstance(vector,list) or len(vector)!=dimensions:raise ValueError('embedding dimension mismatch')
        if not all(type(v) in (int,float) and math.isfinite(v) for v in vector):raise ValueError('non-finite embedding')
        if not any(v!=0 for v in vector):raise ValueError('zero vector has no cosine direction')
    # Preserve ordering: vectors[i] belongs to texts[i]. Count is real provider usage if supplied.
    return {'model':model,'dimensions':dimensions,'vectors':vectors,'input_tokens':data.get('prompt_eval_count')}
async def main():
    result=await embed(['Unopened items: 30 days. Personalized items excluded.','Shipping takes five days.'],
       os.environ['LOCAL_EMBEDDING_MODEL'],int(os.environ['EXPECTED_EMBEDDING_DIMENSIONS']))
    print({'model':result['model'],'dimensions':result['dimensions'],'rows':len(result['vectors']),'input_tokens':result['input_tokens']})
if __name__=='__main__':asyncio.run(main())
