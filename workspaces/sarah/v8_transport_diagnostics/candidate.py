"""Unintegrated diagnostic candidate; frozen V8.1 and its ledgers are unchanged.

No retries, credential loading, new endpoints, response repairs or settlement.
"""
import http.client
import re
import ssl
import time
from workspaces.sarah.repeated_partnership_v8_1.transport import HTTPTransport,TransportFailure


def _classification(error,existing):
    # All output strings are constants or validated HTTP numeric codes.
    if isinstance(existing,str)and re.fullmatch(r'HTTP_[1-5][0-9]{2}',existing):return existing,'http_status'
    if existing in ('TIMEOUT','CONNECTION_FAILURE','INVALID_RESPONSE_JSON'):
        return existing,{'TIMEOUT':'timeout','CONNECTION_FAILURE':'connection','INVALID_RESPONSE_JSON':'response_json'}[existing]
    if isinstance(error,TimeoutError):return 'TIMEOUT','timeout'
    if isinstance(error,http.client.RemoteDisconnected):return 'REMOTE_DISCONNECTED','remote_disconnect'
    if isinstance(error,ConnectionResetError):return 'CONNECTION_RESET','connection_reset'
    if isinstance(error,BrokenPipeError):return 'BROKEN_PIPE','broken_pipe'
    if isinstance(error,http.client.IncompleteRead):return 'INCOMPLETE_RESPONSE','incomplete_read'
    if isinstance(error,ssl.SSLError):return 'TLS_ERROR','tls'
    if isinstance(error,TransportFailure)and error.args==('RESPONSE_TOO_LARGE',):return 'RESPONSE_TOO_LARGE','response_size'
    if not isinstance(error,Exception):return 'INTERRUPTED','interrupted'
    return 'OTHER_TRANSPORT_EXCEPTION','other'


class DiagnosticTransport(HTTPTransport):
    """Preserve transport behavior while adding bounded, value-free diagnostics."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.last_diagnostic={'status':'not_called'}

    def __call__(self,body,timeout):
        started=time.monotonic();self.last_failure=None
        self.last_diagnostic={'status':'in_progress'}
        try:
            result=super().__call__(body,timeout)
        except BaseException as error:
            failure,family=_classification(error,self.last_failure)
            self.last_failure=failure
            self.last_diagnostic={'status':'failed','failure':failure,'exception_family':family,
                                  'elapsed_ms':round(max(0,time.monotonic()-started)*1000)}
            raise
        self.last_diagnostic={'status':'ok','elapsed_ms':round(max(0,time.monotonic()-started)*1000)}
        return result
