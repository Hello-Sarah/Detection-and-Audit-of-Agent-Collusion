from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from threading import Thread
import unittest
from workspaces.sarah.repeated_partnership_v8_1.transport import HTTPTransport,TransportFailure
from workspaces.sarah.repeated_partnership_v8_1.protocol import build_request
from workspaces.sarah.repeated_partnership_v8_1.test_protocol import actor_input,response


class TransportTests(unittest.TestCase):
    def server(self,status=200,redirect=False):
        events=[]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                data=self.rfile.read(int(self.headers['Content-Length']));events.append(data)
                self.send_response(status)
                if redirect:self.send_header('Location','http://127.0.0.1:1/never')
                self.end_headers();self.wfile.write(json.dumps(response()).encode())
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        return 'http://127.0.0.1:'+str(server.server_port)+'/chat',events

    def test_loopback_posts_exact_bytes_once(self):
        url,events=self.server()
        t=HTTPTransport('OFFLINE_FIXTURE_ONLY',_test_url=url)
        prepared=build_request(actor_input())
        self.assertEqual(t(prepared.body,90)['model'],'gpt-5-mini-2025-08-07')
        self.assertEqual(events,[prepared.body])

    def test_redirect_and_http_failure_are_not_retried_or_followed(self):
        for status,redirect in [(302,True),(401,False)]:
            url,events=self.server(status,redirect)
            t=HTTPTransport('OFFLINE_FIXTURE_ONLY',_test_url=url)
            with self.assertRaises(TransportFailure)as caught:t(build_request(actor_input()).body,90)
            self.assertEqual(len(events),1)
            self.assertNotIn('OFFLINE_FIXTURE_ONLY',str(caught.exception))
            self.assertEqual(t.last_failure,'HTTP_'+str(status))

    def test_real_key_cannot_use_test_endpoint(self):
        with self.assertRaises(ValueError):HTTPTransport('not-a-real-key',_test_url='http://127.0.0.1:8000')
        with self.assertRaises(ValueError):HTTPTransport('OFFLINE_FIXTURE_ONLY',_test_url='https://example.com')

if __name__=='__main__':unittest.main()
