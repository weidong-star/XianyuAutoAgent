#!/bin/sh
# Railway ???? ? ???? + ???

python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import os, threading
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.end_headers();self.wfile.write(b'OK')
    def log_message(self,*a):pass
p=int(os.environ.get('PORT',8080))
threading.Thread(target=lambda:HTTPServer(('0.0.0.0',p),H).serve_forever(),daemon=True).start()
print(f'[Railway] Health on :{p}')
" &

exec python3 main.py
