from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import json,tempfile,unittest
from workspaces.sarah.repeated_partnership_v8_1.transport import HTTPTransport
from workspaces.sarah.repeated_partnership_v8_1.test_protocol import response,actor_input
from workspaces.sarah.repeated_partnership_v8_1.budget import BudgetLedger,BoundedDispatcher,BudgetStop

from workspaces.sarah.v8_transport_diagnostics.candidate import DiagnosticTransport as Transport

class CandidateTests(unittest.TestCase):
 def server(self,mode):
  calls=[]
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*a):pass
   def do_POST(self):
    calls.append(self.rfile.read(int(self.headers['Content-Length'])))
    if mode=='disconnect':self.connection.close();return
    self.send_response(int(mode)if mode in ('401','302')else 200)
    if mode=='302':self.send_header('Location','http://127.0.0.1:1/never')
    self.end_headers()
    if mode=='json':self.wfile.write(b'not-json');return
    self.wfile.write(b'x'*2000001 if mode=='oversize'else json.dumps(response()).encode())
  s=ThreadingHTTPServer(('127.0.0.1',0),Handler);t=Thread(target=s.serve_forever,daemon=True);t.start()
  self.addCleanup(t.join);self.addCleanup(s.server_close);self.addCleanup(s.shutdown)
  return 'http://127.0.0.1:'+str(s.server_port),calls
 def test_disconnect_records_constant_diagnostic_once(self):
  url,calls=self.server('disconnect');t=Transport('OFFLINE_FIXTURE_ONLY',_test_url=url)
  with self.assertRaises(Exception):t(b'{}',90)
  self.assertEqual(t.last_failure,'REMOTE_DISCONNECTED');self.assertEqual(len(calls),1)
  self.assertEqual(t.last_diagnostic['exception_family'],'remote_disconnect')
 def test_oversize_records_failure_without_saving_response_content(self):
  url,calls=self.server('oversize');t=Transport('OFFLINE_FIXTURE_ONLY',_test_url=url)
  with self.assertRaises(Exception):t(b'{}',90)
  self.assertEqual(t.last_failure,'RESPONSE_TOO_LARGE');self.assertEqual(len(calls),1)
  self.assertNotIn('OFFLINE_FIXTURE_ONLY',json.dumps(t.last_diagnostic))
 def test_unknown_exception_cannot_echo_arbitrary_message(self):
  t=Transport('OFFLINE_FIXTURE_ONLY')
  class FailingOpener:
   def open(self,*a,**k):raise RuntimeError('SECRET_URL_BODY_AND_KEY')
  t._opener=FailingOpener()
  with self.assertRaises(RuntimeError):t(b'{}',90)
  self.assertEqual(t.last_failure,'OTHER_TRANSPORT_EXCEPTION')
  self.assertNotIn('SECRET',json.dumps(t.last_diagnostic))
 def test_budget_still_holds_unknown_cost_and_blocks_second_dispatch(self):
  url,calls=self.server('disconnect');t=Transport('OFFLINE_FIXTURE_ONLY',_test_url=url)
  with tempfile.TemporaryDirectory()as tmp:
   b=BudgetLedger.create(Path(tmp)/'b.sqlite',cap_nusd=15*10**9,max_requests=128,approval_ref='OFFLINE_FIXTURE_ONLY')
   try:
    d=BoundedDispatcher(b,t)
    with self.assertRaises(BudgetStop):d.dispatch('first',actor_input())
    self.assertEqual(t.last_failure,'REMOTE_DISCONNECTED')
    self.assertTrue(b.summary()['stopped']);self.assertEqual(b.summary()['committed_nusd'],108192000)
    with self.assertRaises(BudgetStop):d.dispatch('second',actor_input())
    self.assertEqual(len(calls),1)
   finally:b.close()
 def test_success_then_failure_resets_diagnostics(self):
  url,calls=self.server('ok');t=Transport('OFFLINE_FIXTURE_ONLY',_test_url=url)
  self.assertEqual(t(b'{}',90)['model'],'gpt-5-mini-2025-08-07')
  self.assertIsNone(t.last_failure)
  self.assertEqual(t.last_diagnostic['status'],'ok')
  class FailingOpener:
   def open(self,*a,**k):raise ConnectionResetError('SECRET')
  t._opener=FailingOpener()
  with self.assertRaises(ConnectionResetError):t(b'{}',90)
  self.assertEqual(t.last_failure,'CONNECTION_RESET')
  self.assertEqual(t.last_diagnostic['status'],'failed')

 def test_http_errors_and_redirects_still_stop_without_retry(self):
  for status in ('401','302'):
   url,calls=self.server(status);t=Transport('OFFLINE_FIXTURE_ONLY',_test_url=url)
   with self.assertRaises(Exception):t(b'{}',90)
   self.assertEqual(t.last_failure,'HTTP_'+status);self.assertEqual(len(calls),1)
   self.assertEqual(t.last_diagnostic['exception_family'],'http_status')
 def test_invalid_json_keeps_original_failure_classification(self):
  url,calls=self.server('json');t=Transport('OFFLINE_FIXTURE_ONLY',_test_url=url)
  with self.assertRaises(Exception):t(b'{}',90)
  self.assertEqual(t.last_failure,'INVALID_RESPONSE_JSON');self.assertEqual(len(calls),1)
 def test_timeout_does_not_echo_error_or_change_exception(self):
  t=Transport('OFFLINE_FIXTURE_ONLY')
  class TimedOut:
   def open(self,*a,**k):raise TimeoutError('SECRET_BODY')
  t._opener=TimedOut()
  with self.assertRaises(TimeoutError):t(b'{}',90)
  self.assertEqual(t.last_failure,'TIMEOUT')
  self.assertNotIn('SECRET',json.dumps(t.last_diagnostic))

 def test_new_call_clears_previous_diagnostic_before_open_and_recovers(self):
  t=Transport('OFFLINE_FIXTURE_ONLY')
  class Failing:
   def open(self,*a,**k):raise ConnectionResetError('SECRET')
  t._opener=Failing()
  with self.assertRaises(ConnectionResetError):t(b'{}',90)
  case=self
  class Result:
   def __enter__(self):return self
   def __exit__(self,*a):return False
   def read(self,*a):return json.dumps(response()).encode()
  class Checking:
   def open(self,*a,**k):
    case.assertEqual(t.last_diagnostic,{'status':'in_progress'})
    case.assertIsNone(t.last_failure)
    return Result()
  t._opener=Checking()
  self.assertEqual(t(b'{}',90)['model'],'gpt-5-mini-2025-08-07')
  self.assertEqual(t.last_diagnostic['status'],'ok')
 def test_specific_faults_preserve_exception_identity_and_redact_details(self):
  import http.client,ssl
  for error,code in [(http.client.IncompleteRead(b'SECRET',10),'INCOMPLETE_RESPONSE'),
                     (BrokenPipeError('SECRET'),'BROKEN_PIPE'),
                     (ssl.SSLError('SECRET'),'TLS_ERROR'),
                     (KeyboardInterrupt('SECRET'),'INTERRUPTED')]:
   t=Transport('OFFLINE_FIXTURE_ONLY')
   class Failing:
    def open(self,*a,**k):raise error
   t._opener=Failing()
   with self.assertRaises(type(error))as caught:t(b'{}',90)
   self.assertIs(caught.exception,error)
   self.assertEqual(t.last_failure,code)
   self.assertNotIn('SECRET',json.dumps(t.last_diagnostic))
 def test_wrapped_tls_remains_generic_connection_diagnostic(self):
  import ssl
  from urllib.error import URLError
  t=Transport('OFFLINE_FIXTURE_ONLY')
  class Failing:
   def open(self,*a,**k):raise URLError(ssl.SSLError('SECRET'))
  t._opener=Failing()
  with self.assertRaises(Exception):t(b'{}',90)
  self.assertEqual(t.last_failure,'CONNECTION_FAILURE')
  self.assertEqual(t.last_diagnostic['exception_family'],'connection')
  self.assertNotIn('SECRET',json.dumps(t.last_diagnostic))

if __name__=='__main__':unittest.main()
