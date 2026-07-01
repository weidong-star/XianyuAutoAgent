#!/bin/bash
# Railway ????
# ???????? HTTP ? XianyuAutoAgent ???

# ???? HTTP ?????Railway ???????
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import os, threading

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b'OK')
    def log_message(self, *a): pass

port = int(os.environ.get('PORT', 8080))
s = HTTPServer(('0.0.0.0', port), H)
print(f'[Railway] Health server on :{port}')
s.serve_forever()
" &

# ?????
exec python main.py
