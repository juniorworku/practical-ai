import asyncio
async def run(limit=2):
    active=peak=0
    semaphore=asyncio.Semaphore(limit)
    async def call(value):
        nonlocal active,peak
        async with semaphore:
            active+=1; peak=max(peak,active)
            try:
                await asyncio.sleep(0)
                if value=='bad': raise TimeoutError('fixture')
                return value.upper()
            finally: active-=1
    results=await asyncio.gather(*(call(v) for v in ['a','bad','c']),return_exceptions=True)
    assert results[0]=='A' and isinstance(results[1],TimeoutError)
    assert results[2]=='C' and peak<=limit and active==0
    return peak
assert asyncio.run(run())==2
print('peak=2; partial failure retained; permits released')

# Bounded exercise variation
assert asyncio.run(run(1))==1
print("Exercise variation: PASS")
