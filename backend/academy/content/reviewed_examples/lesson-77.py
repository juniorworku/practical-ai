import asyncio
async def good(): return 'evidence'
async def bad(): raise TimeoutError('fixture')
async def join():
    results=await asyncio.gather(good(),bad(),return_exceptions=True)
    failures=[type(r).__name__ for r in results if isinstance(r,Exception)]
    return {'status':'partial' if failures else 'completed','failures':failures}
result=asyncio.run(join())
assert result=={'status':'partial','failures':['TimeoutError']}
print('parallel join retained timeout and labeled partial result')

# Bounded exercise variation
release_allowed=result['status']=='completed';assert not release_allowed
print("Exercise variation: PASS")
