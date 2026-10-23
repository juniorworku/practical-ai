import asyncio

async def run(values, operation, workers=3, capacity=2):
    queue=asyncio.Queue(maxsize=capacity);output=[None]*len(values)
    active=peak=queued=0
    async def produce():
        nonlocal queued
        for item in enumerate(values):
            await queue.put(item);queued=max(queued,queue.qsize())
        for _ in range(workers):await queue.put(None)
    async def consume():
        nonlocal active,peak
        while True:
            item=await queue.get()
            try:
                if item is None:return
                index,value=item;active+=1;peak=max(peak,active)
                try:output[index]=await operation(value)
                finally:active-=1
            finally:queue.task_done()
    async with asyncio.TaskGroup() as group:
        group.create_task(produce())
        for _ in range(workers):group.create_task(consume())
    return output,peak,queued,active

async def main():
    # Release index 0 only after index 1 completes: ordering is forced, not timed.
    second=asyncio.Event();finished=[]
    async def operation(value):
        if value==0:await second.wait()
        if value==1:second.set()
        finished.append(value);return value*10
    output,peak,queued,active=await run(list(range(20)),operation)
    assert finished.index(1)<finished.index(0)
    assert output==[n*10 for n in range(20)]
    assert peak<=3 and queued<=2 and active==0
    print('Forced completion disorder; ordered results; peak:',peak,'queue:',queued)
asyncio.run(main())
