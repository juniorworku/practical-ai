"""Real loopback HTTP probes with isolated databases and synthetic keys."""
import asyncio
from contextlib import closing
import http.client
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pipeline import FixtureProvider, ProviderError, Store
from server import Admission, make_server

A='synthetic-owner-a-key-00001'
B='synthetic-owner-b-key-00002'

class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store=Store(str(Path(self.temp.name)/'cache.sqlite3'))
        self.start(FixtureProvider())
    def start(self,provider,**kwargs):
        self.server=make_server({A:'team-a',B:'team-b'},self.store,provider,
            admission=kwargs.pop('admission',Admission(limit=100)),**kwargs)
        self.thread=threading.Thread(target=self.server.serve_forever)
        self.thread.start()
    def stop(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=3)
        self.assertFalse(self.thread.is_alive())
    def tearDown(self): self.stop()
    def request(self,path='/answer',data=None,key=A,raw=None,content_type='application/json'):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        try:
            body=raw if raw is not None else json.dumps(data if data is not None else {'queries':['refund']}).encode()
            headers={'Authorization':'Bearer '+key,'Content-Type':content_type}
            connection.request('POST',path,body,headers)
            response=connection.getresponse()
            return response.status,json.loads(response.read())
        finally:connection.close()
    def test_health_and_owner_contract(self):
        with closing(http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)) as conn:
            conn.request('GET','/health'); response=conn.getresponse()
            self.assertEqual(response.status,200);self.assertFalse(json.loads(response.read())['provider_checked'])
        status,result=self.request(data={'queries':['refund','unknown']})
        self.assertEqual(status,200)
        self.assertEqual([r['source'] for r in result['results']],['a-refunds-v1',None])
        self.assertIsNone(self.request(key=B)[1]['results'][0]['source'])
    def test_bad_requests(self):
        for kwargs,status in [({'key':'invalid'},401),({'path':'/missing'},404),
            ({'data':{'queries':['refund'],'owner':'team-b'}},400),({'data':{'queries':[]}},400),
            ({'data':{'queries':['refund',None]}},400),({'raw':b'{broken'},400),
            ({'raw':b'\xff'},400),({'raw':b'x'*16385},413),({'content_type':'text/plain'},415)]:
            with self.subTest(kwargs=kwargs):self.assertEqual(self.request(**kwargs)[0],status)
        with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM cache').fetchone()[0],0)
    def test_replaced_server_reads_committed_state(self):
        self.assertFalse(self.request()[1]['results'][0]['cached'])
        self.stop();self.store=Store(self.store.path);self.start(FixtureProvider())
        self.assertTrue(self.request()[1]['results'][0]['cached'])
    def test_quota_and_clock_recovery_without_sleep(self):
        self.stop();now=[0.0]
        admission=Admission(limit=2,clock=lambda:now[0])
        self.start(FixtureProvider(),admission=admission)
        self.assertEqual(self.request()[0],200);self.assertEqual(self.request()[0],200)
        self.assertEqual(self.request()[0],429)
        self.assertEqual(self.request(key=B)[0],200)
        now[0]=60
        self.assertEqual(self.request()[0],200)
    def test_provider_fault_is_502_not_bad_client_input(self):
        self.stop()
        class Broken:
            identity='broken'
            async def answer(self,*args):raise ProviderError('synthetic invalid upstream')
        self.start(Broken())
        self.assertEqual(self.request()[0],502)
        with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM cache').fetchone()[0],0)
    def test_provider_timeout_is_504_and_slot_recovers(self):
        self.stop();cleaned=threading.Event()
        class Slow:
            identity='slow'
            async def answer(self,*args):
                try:await asyncio.Event().wait()
                finally:cleaned.set()
        controls=Admission(limit=100,capacity=1)
        self.start(Slow(),admission=controls,item_deadline=.1,deadline=1)
        self.assertEqual(self.request()[0],504);self.assertTrue(cleaned.is_set())
        self.assertTrue(controls.slots.acquire(blocking=False));controls.slots.release()
    def test_capacity_rejection_and_release(self):
        self.stop();started=threading.Event();release=threading.Event()
        class Held:
            identity='held'
            async def answer(self,query,evidence):
                started.set()
                while not release.is_set():await asyncio.sleep(.01)
                return await FixtureProvider().answer(query,evidence)
        self.start(Held(),admission=Admission(limit=100,capacity=1))
        with ThreadPoolExecutor(max_workers=1) as pool:
            first=pool.submit(self.request)
            try:
                self.assertTrue(started.wait(timeout=3))
                self.assertEqual(self.request()[0],503)
            finally:release.set()
            self.assertEqual(first.result(timeout=5)[0],200)
        self.assertEqual(self.request()[0],200)

if __name__=='__main__':unittest.main()
