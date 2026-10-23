import threading

class Window:
    def __init__(self,clock,limit=2,window=60):
        self.clock=clock;self.limit=limit;self.window=window;self.events={};self.lock=threading.Lock()
    def allow(self,owner):
        with self.lock:
            now=self.clock()
            recent=[t for t in self.events.get(owner,[]) if now-t<self.window]
            if len(recent)>=self.limit:return False
            self.events[owner]=[*recent,now];return True

now=[0];quota=Window(lambda:now[0]);slots=threading.BoundedSemaphore(1)
assert quota.allow('a') and quota.allow('a') and not quota.allow('a')
assert quota.allow('b'), 'one owner must not consume another owner quota'
now[0]=60;assert quota.allow('a')
assert slots.acquire(blocking=False)
try:
    assert not slots.acquire(blocking=False), 'capacity is independent from rate'
finally:slots.release()
assert slots.acquire(blocking=False);slots.release()
print('Per-owner window boundary and slot recovery checked without a minute-long sleep')
# The HTTP project wires these separate controls into real requests. Python locks
# protect one process; neither these dictionaries nor slots span replicas.
