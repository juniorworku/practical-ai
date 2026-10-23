import asyncio

class SingleFlight:
    def __init__(self):self.pending={}
    async def get(self,key,compute):
        task=self.pending.get(key)
        if task is None:
            task=asyncio.create_task(compute())
            self.pending[key]=task
            def done(completed):
                if self.pending.get(key) is completed:self.pending.pop(key,None)
                if not completed.cancelled():completed.exception()  # Retrieve abandoned failures.
            task.add_done_callback(done)
        # Cancelling one waiter must not cancel the result needed by another.
        return await asyncio.shield(task)
    async def close(self):
        tasks=list(self.pending.values())
        for task in tasks:task.cancel()
        await asyncio.gather(*tasks,return_exceptions=True)
        self.pending.clear()

async def main():
    service=SingleFlight();entered=asyncio.Event();release=asyncio.Event();calls=0
    async def compute():
        nonlocal calls
        calls+=1;entered.set();await release.wait();return 'answer'
    first=asyncio.create_task(service.get(('owner-a','revision-v1'),compute))
    await entered.wait()
    second=asyncio.create_task(service.get(('owner-a','revision-v1'),compute))
    try:
        await asyncio.sleep(0);first.cancel()
        try:await first
        except asyncio.CancelledError:pass
        release.set()
        assert await second=='answer' and calls==1
    finally:await service.close()
    assert not service.pending
    print('One computation, cancellation-isolated waiters and explicit service cleanup')
asyncio.run(main())
# This registry coalesces in-flight work only. Durable caching and distributed
# coordination are separate layers; keys must already include owner/revisions.
