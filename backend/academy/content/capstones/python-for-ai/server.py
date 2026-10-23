"""Single-process local teaching service; no production hosting claim."""
import asyncio
import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pipeline import FixtureProvider, OllamaProvider, Store, InputError, ProviderError, answer_batch

class Admission:
    def __init__(self, limit=10, window=60, capacity=2, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.lock = threading.Lock()
        self.windows = {}
        self.slots = threading.BoundedSemaphore(capacity)
    def allow(self, owner):
        with self.lock:
            now = self.clock()
            recent = [t for t in self.windows.get(owner, []) if now-t < self.window]
            if len(recent) >= self.limit:
                return False
            self.windows[owner] = [*recent, now]
            return True

def error_status(error):
    if isinstance(error, ExceptionGroup):
        statuses = [error_status(child) for child in error.exceptions]
        return 504 if 504 in statuses else 502 if 502 in statuses else 400
    if isinstance(error, TimeoutError): return 504
    if isinstance(error, InputError): return 400
    return 502

def make_server(keys, store, provider, *, host="127.0.0.1", port=0, admission=None, deadline=25, item_deadline=18):
    if not isinstance(keys, dict) or not keys or any(not isinstance(k, str) or len(k) < 20 or not isinstance(v,str) or v not in {"team-a", "team-b"} for k,v in keys.items()):
        raise ValueError("Map random keys of at least 20 characters to team-a or team-b")
    controls = admission or Admission()
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)  # Also bounds waiting for headers.
        def log_message(self, *_): pass  # Never log keys or question bodies.
        def send_json(self, status, payload):
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            if self.path != "/health": return self.send_json(404, {"error":"Not found"})
            try:
                with store.connect() as db: db.execute("SELECT 1 FROM cache LIMIT 1")
            except Exception: return self.send_json(503, {"ready":False})
            self.send_json(200, {"ready":True, "provider":provider.identity, "provider_checked":False})
        def do_POST(self):
            if self.path != "/answer": return self.send_json(404, {"error":"Not found"})
            auth = self.headers.get("Authorization", "").encode()
            owner = next((v for k,v in keys.items() if hmac.compare_digest(auth, ("Bearer "+k).encode())), None)
            if owner is None: return self.send_json(401, {"error":"Invalid credentials"})
            if not controls.allow(owner): return self.send_json(429, {"error":"Owner request quota exhausted"})
            if not controls.slots.acquire(blocking=False): return self.send_json(503, {"error":"At capacity"})
            try:
                lengths = self.headers.get_all("Content-Length", [])
                if self.headers.get("Transfer-Encoding") or len(lengths) != 1:
                    return self.send_json(400, {"error":"Use one Content-Length; chunked requests are unsupported"})
                raw = lengths[0]
                if len(raw) > 5 or not raw.isascii() or not raw.isdigit() or not 0 < int(raw) <= 16384:
                    return self.send_json(413, {"error":"Send at most 16 KiB"})
                if self.headers.get_content_type() != "application/json":
                    return self.send_json(415, {"error":"Expected application/json"})
                body = self.rfile.read(int(raw))
                if len(body) != int(raw): return self.send_json(400, {"error":"Truncated request"})
                try: data = json.loads(body)
                except (ValueError, UnicodeError): return self.send_json(400, {"error":"Invalid JSON"})
                if not isinstance(data, dict) or set(data) != {"queries"}:
                    return self.send_json(400, {"error":"Expected only queries; identity comes from credentials"})
                try:
                    result = asyncio.run(answer_batch(owner, data["queries"], provider, store,
                        deadline=deadline, item_deadline=item_deadline))
                except Exception as error:
                    return self.send_json(error_status(error), {"error":"Request failed; no completed batch claimed"})
                return self.send_json(200, {"results":result})
            except TimeoutError:
                return self.send_json(408, {"error":"Request body timed out"})
            finally:
                controls.slots.release()
    return ThreadingHTTPServer((host, port), Handler)

if __name__ == "__main__":
    try:
        keys = json.loads(os.environ.get("STUDENT_KEYS", "{}"))
        provider = OllamaProvider(os.environ.get("OLLAMA_MODEL", "")) if os.environ.get("PROVIDER") == "ollama" else FixtureProvider()
        server = make_server(keys, Store(os.environ.get("STATE_PATH", "state/cache.sqlite3")), provider,
            host=os.environ.get("BIND_HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8094")))
    except ValueError as error:
        raise SystemExit(str(error))
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
