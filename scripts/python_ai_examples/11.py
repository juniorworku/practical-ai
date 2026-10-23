import json
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def do_GET(self):
        body = json.dumps({'ready':True,'provider_checked':False}).encode()
        self.send_response(200 if self.path == '/health' else 404)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

server = HTTPServer(('127.0.0.1',0),Handler)
worker = threading.Thread(target=server.serve_forever)
worker.start()
try:
    with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/health',timeout=2) as response:
        result = json.load(response)
    assert result == {'ready':True,'provider_checked':False}
    print('HTTP readiness contract:',result)
finally:
    server.shutdown()
    server.server_close()
    worker.join(timeout=2)
    assert not worker.is_alive()
