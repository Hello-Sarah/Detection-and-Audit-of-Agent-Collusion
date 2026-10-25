"""Local fixture only. No model endpoint or credentials."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from workspaces.sarah.repeated_partnership_v8_1.transport import HTTPTransport
from pathlib import Path
import json

out=[]
for mode in ('disconnect','oversize'):
 events=[]
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   events.append(self.rfile.read(int(self.headers['Content-Length'])))
   if mode=='disconnect':self.connection.close();return
   self.send_response(200);self.end_headers();self.wfile.write(b'x'*2000001)
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
 thread=Thread(target=server.serve_forever,daemon=True);thread.start()
 t=HTTPTransport('OFFLINE_FIXTURE_ONLY',_test_url='http://127.0.0.1:'+str(server.server_port))
 try:t(b'{}',90)
 except Exception as e:out.append({'fixture':mode,'exception_class':type(e).__name__,'last_failure':t.last_failure,'requests_seen':len(events)})
 finally:server.shutdown();server.server_close();thread.join()
p=Path('workspaces/sarah/v8_transport_diagnostics');p.mkdir(exist_ok=True)
(p/'REPRODUCED_GAPS.json').write_text(json.dumps({'run_type':'local_scripted_faults_not_live_replay','model_api_calls':0,'results':out},indent=2)+'\n')
print(json.dumps(out))
