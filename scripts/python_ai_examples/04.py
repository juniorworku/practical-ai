import asyncio

async def main():
    cleaned = asyncio.Event()
    async def provider():
        try:
            await asyncio.sleep(60)
            return 'unreachable'
        finally:
            cleaned.set()
    try:
        async with asyncio.timeout(0.02):
            await provider()
    except TimeoutError:
        assert cleaned.is_set()
        print('Deadline propagated cancellation and ran cleanup')
    else:
        raise AssertionError('deadline not enforced')
    # Cancellation is cooperative. A CPU loop with no awaits blocks this deadline.
asyncio.run(main())
