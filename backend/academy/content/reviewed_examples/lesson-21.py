import json,threading,urllib.request,urllib.error
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        status=200 if self.path=='/health' else 404
        body=json.dumps({'status':'ok'} if status==200 else {'error':'not_found'}).encode()
        self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever);thread.start()
base=f'http://127.0.0.1:{server.server_port}'
try:
    assert json.load(urllib.request.urlopen(base+'/health'))=={'status':'ok'}
    try: urllib.request.urlopen(base+'/missing')
    except urllib.error.HTTPError as error: assert error.code==404
    else: raise AssertionError('missing route succeeded')
finally: server.shutdown();thread.join();server.server_close()
print('real loopback health=200; unknown path=404')

# Bounded exercise variation
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever);thread.start()
try:
    try: urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/another-missing-path')
    except urllib.error.HTTPError as error:
        assert error.code==404 and json.load(error)=={'error':'not_found'}
    else: raise AssertionError('unknown path succeeded')
finally: server.shutdown();thread.join();server.server_close()
print("Exercise variation: PASS")
