import asyncio

class TransientRead(Exception):
    def __init__(self,retry_after=0):self.retry_after=retry_after

async def safe_read(call, clock, sleep, *, budget=1.0, attempts=3):
    end=clock()+budget
    for number in range(attempts):
        if clock()>=end:raise TimeoutError('overall budget')
        try:return await call()
        except TransientRead as error:
            if number+1==attempts:raise
            delay=max(.1*2**number,error.retry_after)
            if delay>=end-clock():raise TimeoutError('backoff would consume budget')
            await sleep(delay)

async def main():
    now=[0.0];waits=[];calls=0
    def clock():return now[0]
    async def sleep(delay):waits.append(delay);now[0]+=delay
    async def flaky():
        nonlocal calls
        calls+=1
        if calls<3:raise TransientRead(.25)
        return 'policy-v1'
    assert await safe_read(flaky,clock,sleep)=='policy-v1'
    assert waits==[.25,.25] and calls==3
    async def unavailable():raise TransientRead(2)
    try:await safe_read(unavailable,clock,sleep)
    except TimeoutError:pass
    else:raise AssertionError('Retry-After exceeded budget')
    assert waits==[.25,.25], 'do not sleep when there is no remaining allowance'
    print('Injected clock proves attempt and backoff policy without timing guesses')
asyncio.run(main())
# The real call also needs an async timeout: a fake policy clock cannot interrupt I/O.
