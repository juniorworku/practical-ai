import asyncio

async def map_bounded(values, workers=2, operation=None):
    async def double(value):
        await asyncio.sleep(0)
        return value * 2
    operation = operation or double
    queue = asyncio.Queue(maxsize=2)
    results = [None] * len(values)
    active = peak = 0
    async def produce():
        for item in enumerate(values):
            await queue.put(item)
        for _ in range(workers):
            await queue.put(None)
    async def consume():
        nonlocal active, peak
        while True:
            item = await queue.get()
            try:
                if item is None: return
                index, value = item
                active += 1
                peak = max(peak, active)
                try:
                    results[index] = await operation(value)
                finally: active -= 1
            finally: queue.task_done()
    async with asyncio.TaskGroup() as group:
        group.create_task(produce())
        for _ in range(workers): group.create_task(consume())
    return results, peak

async def main():
    results, peak = await map_bounded(list(range(20)))
    assert results == [n*2 for n in range(20)]
    assert peak <= 2
    print('Ordered outputs and measured peak:', results, peak)
asyncio.run(main())
