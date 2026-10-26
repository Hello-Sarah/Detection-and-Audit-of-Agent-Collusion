"""DNS-only diagnostic. No HTTP, API client, credentials or model requests."""
import argparse
from datetime import datetime, timezone
import json
import os
import socket
import time


def probe(context):
    result = {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'tool_execution_context': context,
        'scope': 'Address resolution only; no HTTP, TCP/TLS probe or model call',
        'sandbox_network_disabled_flag': os.environ.get('CODEX_SANDBOX_NETWORK_DISABLED') == '1',
        'dns': [],
    }
    for host in ('localhost', 'api.openai.com', 'github.com', 'example.com'):
        start = time.monotonic()
        try:
            rows = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
            item = {'host': host, 'status': 'resolved', 'address_count': len(rows)}
        except OSError as error:
            item = {'host': host, 'status': 'failed',
                    'exception_type': type(error).__name__, 'errno': error.errno}
        item['elapsed_ms'] = round((time.monotonic() - start) * 1000)
        result['dns'].append(item)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True, choices=('use_default', 'require_escalated'))
    print(json.dumps(probe(parser.parse_args().context), indent=2))
