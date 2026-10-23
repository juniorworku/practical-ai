import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx
import pipeline
from pipeline import FixtureProvider, Reply, Store, InputError, ProviderError, OllamaProvider, answer_batch, answer_one

class PipelineTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(str(Path(self.temp.name)/"cache.sqlite3"))
        self.provider = FixtureProvider()
    def row_count(self):
        with self.store.connect() as db: return db.execute("SELECT count(*) FROM cache").fetchone()[0]
    async def test_owner_and_abstention(self):
        a = await answer_one("team-a", "refund days?", self.provider, self.store)
        b = await answer_one("team-b", "refund days?", self.provider, self.store)
        self.assertEqual(a["source"], "a-refunds-v1")
        self.assertIsNone(b["source"])
        self.assertEqual(b["provider"], "not-called")
    async def test_cache_survives_reopen(self):
        await answer_one("team-a", "refund", self.provider, self.store)
        result = await answer_one("team-a", "refund", self.provider, Store(self.store.path))
        self.assertTrue(result["cached"])
    async def test_batch_order(self):
        result = await answer_batch("team-a", ["refund", "unknown", "days"], self.provider, self.store)
        self.assertEqual([r["source"] for r in result], ["a-refunds-v1", None, "a-refunds-v1"])
    async def test_invalid_input_before_any_work(self):
        for queries in [[], ["a"]*21, "refund", ["refund",None], ["refund"," "], ["x"*2001]]:
            with self.assertRaises(InputError):
                await answer_batch("team-a", queries, self.provider, self.store)
            self.assertEqual(self.row_count(), 0)
        for workers in [True,0,5,1.5]:
            with self.assertRaises(InputError):
                await answer_batch("team-a", ["refund"], self.provider, self.store, workers=workers)
    async def test_invalid_provider_never_cached(self):
        for value in [Reply("wrong","other-owner"), Reply("", "a-refunds-v1"),
                      Reply("x","a-refunds-v1",True,0), Reply("x","a-refunds-v1",-1,0), {"text":"wrong type"}]:
            class Bad:
                identity = "bad"
                async def answer(self, query, evidence): return value
            with self.assertRaises(ProviderError): await answer_one("team-a", "refund", Bad(), self.store)
            self.assertEqual(self.row_count(), 0)
    async def test_cancel_propagates_and_cleans_every_worker(self):
        started = asyncio.Event()
        active = 0
        class Slow:
            identity = "slow"
            async def answer(self, query, evidence):
                nonlocal active
                active += 1; started.set()
                try: await asyncio.Event().wait()
                finally: active -= 1
        job = asyncio.create_task(answer_batch("team-a", ["refund"]*20, Slow(), self.store))
        await started.wait(); job.cancel()
        with self.assertRaises(asyncio.CancelledError): await job
        self.assertEqual(active, 0)
        self.assertEqual(self.row_count(), 0)
    async def test_deadline_does_not_cache_partial_answer(self):
        cleaned = asyncio.Event()
        class Slow:
            identity = "deadline"
            async def answer(self, query, evidence):
                try: await asyncio.Event().wait()
                finally: cleaned.set()
        with self.assertRaises(TimeoutError):
            await answer_one("team-a", "refund", Slow(), self.store, deadline=.1)
        self.assertTrue(cleaned.is_set())
        self.assertEqual(self.row_count(), 0)
    async def test_batch_failure_cancels_siblings(self):
        started = asyncio.Event(); cleaned = asyncio.Event()
        class Failing:
            identity = "failing"
            async def answer(self, query, evidence):
                if query == "refund fail":
                    await started.wait(); raise ProviderError("synthetic outage")
                started.set()
                try: await asyncio.Event().wait()
                finally: cleaned.set()
        with self.assertRaises(ExceptionGroup):
            await answer_batch("team-a", ["refund","refund fail"]*5, Failing(), self.store)
        self.assertTrue(cleaned.is_set())
    async def test_model_source_prompt_invalidate_independently(self):
        await answer_one("team-a", "refund", self.provider, self.store)
        other = FixtureProvider(); other.identity = "revised-v2"
        self.assertFalse((await answer_one("team-a", "refund", other, self.store))["cached"])
        with patch.dict(pipeline.DOCUMENTS, {"team-a":{**pipeline.DOCUMENTS["team-a"], "id":"a-refunds-v2"}}):
            self.assertFalse((await answer_one("team-a", "refund", self.provider, self.store))["cached"])
        with patch.object(pipeline,"REVISION","policy-v1:prompt-v3:reply-v2"):
            self.assertFalse((await answer_one("team-a", "refund", self.provider, self.store))["cached"])
    async def test_consistent_backup_and_restore(self):
        await answer_one("team-a", "refund", self.provider, self.store)
        target = str(Path(self.temp.name)/"restored.sqlite3")
        await asyncio.to_thread(self.store.backup,target)
        self.assertTrue((await answer_one("team-a", "refund", self.provider, Store(target)))["cached"])
        self.assertIsNone((await answer_one("team-b","refund",self.provider,Store(target)))["source"])
    async def test_unknown_usage_remains_unknown(self):
        result = await answer_one("team-a","refund",self.provider,self.store)
        self.assertEqual(result["usage"],{"input_tokens":None,"output_tokens":None})

    async def test_batch_deadline_includes_queued_work(self):
        active=0
        class Slow:
            identity='batch-deadline'
            async def answer(self,*args):
                nonlocal active
                active+=1
                try:await asyncio.Event().wait()
                finally:active-=1
        with self.assertRaises(TimeoutError):
            await answer_batch('team-a',['refund']*20,Slow(),self.store,deadline=.2,item_deadline=5)
        self.assertEqual(active,0)
        self.assertEqual(self.row_count(),0)
    async def test_actual_peak_stays_within_worker_bound(self):
        active=peak=calls=0
        class Counting:
            identity='counting'
            async def answer(self,query,evidence):
                nonlocal active,peak,calls
                active+=1;calls+=1;peak=max(peak,active)
                try:
                    await asyncio.sleep(.01)
                    return Reply(evidence['text'],evidence['id'])
                finally:active-=1
        queries=['refund '+str(n) for n in range(20)]
        original=list(queries)
        result=await answer_batch('team-a',queries,Counting(),self.store,workers=3)
        self.assertEqual(len(result),20)
        self.assertEqual(calls,20)
        self.assertLessEqual(peak,3)
        self.assertEqual(active,0)
        self.assertEqual(queries,original)

class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_httpx_request_and_validated_usage(self):
        def respond(request):
            payload = json.loads(request.content)
            self.assertEqual(payload["model"], "installed-test-tag")
            self.assertFalse(payload["stream"])
            return httpx.Response(200,json={"done":True,"message":{"content":"14 days"},"prompt_eval_count":9,"eval_count":3})
        provider = OllamaProvider("installed-test-tag",transport=httpx.MockTransport(respond))
        reply = await provider.answer("refund", pipeline.DOCUMENTS["team-a"])
        self.assertEqual(reply,Reply("14 days","a-refunds-v1",9,3))
    async def test_httpx_failure_matrix(self):
        bodies=[[],{"done":False},{"done":True,"message":[]},{"done":True,"message":{"content":""}},
                {"done":True,"message":{"content":"ok"},"eval_count":True},
                {"done":True,"message":{"content":"x"*8001}}]
        responses=[httpx.Response(503),httpx.Response(200,content=b'{bad'),httpx.Response(200,content=b'x'*65537)]
        responses += [httpx.Response(200,json=body) for body in bodies]
        for response in responses:
            with self.subTest(response=response):
                provider = OllamaProvider("test",transport=httpx.MockTransport(lambda request:response))
                with self.assertRaises(ProviderError): await provider.answer("refund",pipeline.DOCUMENTS["team-a"])

if __name__ == "__main__": unittest.main()
