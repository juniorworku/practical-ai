import asyncio
import threading

async def main():
    entered=threading.Event();release=threading.Event();finished=threading.Event()
    def blocking_work():
        entered.set()
        try:release.wait(timeout=3)
        finally:finished.set()
    job=asyncio.create_task(asyncio.to_thread(blocking_work))
    try:
        assert await asyncio.to_thread(entered.wait,2)
        job.cancel()
        try:await job
        except asyncio.CancelledError:pass
        else:raise AssertionError('cancellation swallowed')
        assert not finished.is_set(), 'a cancelled await does not terminate a running thread'
    finally:
        release.set()
        assert await asyncio.to_thread(finished.wait,2)
    print('Cancelled coroutine; underlying thread required its own release/timeout')
asyncio.run(main())
