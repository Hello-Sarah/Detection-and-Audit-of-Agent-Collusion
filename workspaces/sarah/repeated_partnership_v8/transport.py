"""Explicit fixed-endpoint HTTP transport. Never instantiated with a real key by tests."""
import json
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse
from urllib.request import Request,build_opener,HTTPRedirectHandler

ENDPOINT='https://api.openai.com/v1/chat/completions'


class TransportFailure(RuntimeError):pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None


class HTTPTransport:
    def __init__(self,api_key,*,_test_url=None):
        if not isinstance(api_key,str)or not api_key:raise ValueError('API key required')
        self._key=api_key;self.endpoint=ENDPOINT;self.last_failure=None
        if _test_url is not None:
            parsed=urlparse(_test_url)
            if api_key!='OFFLINE_FIXTURE_ONLY'or parsed.scheme!='http'or parsed.hostname!='127.0.0.1' or parsed.username or parsed.password:
                raise ValueError('Only fixture key and loopback test URL allowed')
            self.endpoint=_test_url
        self._opener=build_opener(NoRedirect())

    def __call__(self,body,timeout):
        if not isinstance(body,bytes)or timeout!=90:raise ValueError('Pinned bytes/90second transport required')
        self.last_failure=None
        request=Request(self.endpoint,data=body,headers={'Authorization':'Bearer '+self._key,'Content-Type':'application/json'},method='POST')
        try:
            with self._opener.open(request,timeout=timeout)as result:
                raw=result.read(2000001)
                if len(raw)>2000000:raise TransportFailure('RESPONSE_TOO_LARGE')
                return json.loads(raw.decode('utf-8'))
        except HTTPError as exc:
            self.last_failure='HTTP_'+str(exc.code)
            exc.close()
            raise TransportFailure(self.last_failure)from None
        except TimeoutError:
            self.last_failure='TIMEOUT'
            raise
        except URLError as exc:
            if isinstance(exc.reason,TimeoutError):
                self.last_failure='TIMEOUT';raise TimeoutError('TIMEOUT')from None
            self.last_failure='CONNECTION_FAILURE'
            raise TransportFailure(self.last_failure)from None
        except (UnicodeDecodeError,json.JSONDecodeError):
            self.last_failure='INVALID_RESPONSE_JSON'
            raise TransportFailure(self.last_failure)from None
