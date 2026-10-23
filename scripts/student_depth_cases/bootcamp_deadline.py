"""Read-only retries: executable fixture transport, no provider calls."""
import asyncio

class Transient(Exception):
    pass

class Permanent(Exception):
    pass

async def generate(transport, *, budget=.2, attempts=3):
    if budget <= 0 or type(attempts) is not int or not 1 <= attempts <= 5:
        raise ValueError('bounded deadline and attempts required')
    # The outer deadline includes execution, waiting and backoff.
    async with asyncio.timeout(budget):
        for number in range(attempts):
            try:
                return await transport()
            except Transient:
                if number + 1 == attempts:
                    raise
                await asyncio.sleep(min(.001 * 2 ** number, .01))
    raise AssertionError('unreachable')

async def demonstrate():
    calls = 0
    async def transient_then_ok():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise Transient('fixture unavailable')
        return {'status': 'draft', 'usage': None}
    assert (await generate(transient_then_ok))['status'] == 'draft'
    assert calls == 2
    async def unauthenticated():
        raise Permanent('fixture credentials rejected')
    try:
        await generate(unauthenticated)
    except Permanent:
        pass
    else:
        raise AssertionError('permanent failure was hidden')
    entered = asyncio.Event()
    cleaned = asyncio.Event()
    async def blocked():
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()
    try:
        await generate(blocked, budget=.02)
    except TimeoutError:
        pass
    else:
        raise AssertionError('deadline ignored')
    assert entered.is_set() and cleaned.is_set()
    print('transient: 2 calls; permanent: propagated; deadline: cleanup completed')

if __name__ == '__main__':
    asyncio.run(demonstrate())
