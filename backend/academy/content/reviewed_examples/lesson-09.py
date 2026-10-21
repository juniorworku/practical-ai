import asyncio
class Fake:
    async def generate(self,passages):
        return {'text':passages[0] if passages else 'Insufficient evidence','model':'fake','usage':None}
class Offline:
    async def generate(self,passages): raise TimeoutError('unavailable')
async def check():
    assert (await Fake().generate(['14 days']))['model']=='fake'
    try: await Offline().generate([])
    except TimeoutError: pass
    else: raise AssertionError('outage masked')
asyncio.run(check())
print('provider contract kept; outage propagated')

# Bounded exercise variation
assert asyncio.run(Fake().generate([]))['usage'] is None
print("Exercise variation: PASS")
