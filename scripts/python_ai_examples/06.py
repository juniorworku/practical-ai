import asyncio

class TransientRead(Exception): pass

async def retry_read(call, attempts=3, pause=0.001):
    if not 1 <= attempts <= 5: raise ValueError('invalid retry budget')
    for index in range(attempts):
        try: return await call()
        except TransientRead:
            if index + 1 == attempts: raise
            await asyncio.sleep(pause * 2**index)

async def main():
    calls = 0
    async def flaky():
        nonlocal calls
        calls += 1
        if calls < 3: raise TransientRead('synthetic 503')
        return 'policy-v1'
    async with asyncio.timeout(1):
        assert await retry_read(flaky) == 'policy-v1'
    assert calls == 3
    async def forbidden(): raise PermissionError('401: do not retry')
    try: await retry_read(forbidden)
    except PermissionError: print('Permission failure surfaced immediately')
    else: raise AssertionError('permission failure became success')
    print('Bounded safe-read attempts:', calls)
asyncio.run(main())
