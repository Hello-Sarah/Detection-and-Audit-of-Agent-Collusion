"""Read-only evidence/config audit and in-memory failure fixtures. No networking."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
import ssl
import stat
import subprocess
import sys
import tempfile
from urllib.error import URLError
from urllib.request import getproxies

from workspaces.sarah.followup_task_structure_v10.collector import verify
from workspaces.sarah.repeated_partnership_v8_1.budget import BudgetLedger, BoundedDispatcher, BudgetStop
from workspaces.sarah.repeated_partnership_v8_1.technical import _settings, validate_runtime
from workspaces.sarah.repeated_partnership_v8_1.test_protocol import actor_input
from workspaces.sarah.repeated_partnership_v8_1.transport import ENDPOINT
from workspaces.sarah.v8_transport_diagnostics.candidate import DiagnosticTransport

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'workspaces/sarah/experiment_runs/2026-10-26/task_structure_v10_01'
FREEZE = ROOT / 'workspaces/sarah/followup_task_structure_v10/execution_freeze_01'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FailingOpener:
    def __init__(self, error):
        self.error = error
        self.calls = 0

    def open(self, *args, **kwargs):
        self.calls += 1
        raise self.error


def audit():
    validate_runtime()
    settings = _settings()
    verify(FREEZE / 'EXECUTION_MANIFEST.json')
    hashes = json.loads((RUN / 'evidence_hashes.json').read_text())
    before = {rel: sha(RUN / rel) for rel in hashes}
    assert before == hashes
    db = sqlite3.connect((RUN / 'budget.sqlite').resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        states = db.execute('SELECT state,COUNT(*),SUM(committed_nusd) FROM reservations GROUP BY state').fetchall()
        metadata = db.execute('SELECT cap_nusd,max_requests,stopped FROM metadata').fetchone()
        usage = db.execute('SELECT COUNT(raw_response),COUNT(prompt_tokens),COUNT(completion_tokens) FROM reservations').fetchone()
    finally:
        db.close()
    trace = [json.loads(line) for line in (RUN / 'v10_b1_d1m0/trajectory.jsonl').read_text().splitlines()]
    transport = [json.loads(line) for line in (RUN / 'transport.jsonl').read_text().splitlines()]
    response_count = sum(e['kind'] == 'provider_response' for e in trace)
    assert response_count == 0
    fixtures = []
    for name, reason in [('dns', socket.gaierror(8, 'OFFLINE_FIXTURE')),
                         ('wrapped_tls', ssl.SSLError('OFFLINE_FIXTURE'))]:
        client = DiagnosticTransport('OFFLINE_FIXTURE_ONLY')
        client._opener = FailingOpener(URLError(reason))
        try:
            client(b'{}', 90)
            raise AssertionError('Expected fixture failure')
        except RuntimeError as error:
            fixtures.append({'fixture': name, 'reason_type_in_fixture': type(reason).__name__,
                             'raised_type': type(error).__name__, 'diagnostic': client.last_diagnostic})
        assert client.last_failure == 'CONNECTION_FAILURE'
    with tempfile.TemporaryDirectory() as temp:
        ledger = BudgetLedger.create(Path(temp) / 'fixture.sqlite', cap_nusd=10**9,
                                     max_requests=2, approval_ref='OFFLINE_FIXTURE_ONLY')
        client = DiagnosticTransport('OFFLINE_FIXTURE_ONLY')
        opener = FailingOpener(URLError(socket.gaierror(8, 'OFFLINE_FIXTURE')))
        client._opener = opener
        dispatcher = BoundedDispatcher(ledger, client)
        failures = []
        try:
            for call_id in ('fixture_first', 'fixture_second'):
                try:
                    dispatcher.dispatch(call_id, actor_input())
                    raise AssertionError('Expected budget stop')
                except BudgetStop as error:
                    failures.append(str(error))
            guard = {'transport_open_calls': opener.calls, 'stop_codes': failures, 'ledger': ledger.summary()}
            assert opener.calls == 1 and guard['ledger']['request_count'] == 1
            assert guard['ledger']['stopped'] is True
        finally:
            ledger.close()
    assert {rel: sha(RUN / rel) for rel in hashes} == before
    dotenv = ROOT / '.env'
    return {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'No network operations; fixture opener replaces HTTP opening; no real credentials sent',
        'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
        'runtime': {'python': sys.version.split()[0], 'runtime_validation': 'pass',
                    'key_configured': bool(settings.get('OPENAI_API_KEY')),
                    'model': settings.get('OPENAI_MODEL'), 'base_url': settings.get('OPENAI_BASE_URL'),
                    'transport_endpoint': ENDPOINT, 'dotenv_mode': oct(stat.S_IMODE(dotenv.stat().st_mode)),
                    'dotenv_ignored': subprocess.run(['git', 'check-ignore', '-q', '.env'], cwd=ROOT).returncode == 0,
                    'proxy_schemes_present': sorted(getproxies()),
                    'certificate_paths_exist': {k: bool(v and Path(v).exists())
                        for k, v in ssl.get_default_verify_paths()._asdict().items() if k in ('cafile', 'capath')}},
        'v10_evidence': {'original_hashes_verified': len(hashes), 'unchanged_after_audit': True,
                         'frozen_source_data_bundle_verified': True,
                         'event_kind_counts': dict(Counter(e['kind'] for e in trace)),
                         'transport': transport, 'provider_response_count': response_count},
        'v10_ledger': {'states': states, 'metadata_cap_requests_stopped': metadata,
                       'response_prompt_completion_field_counts': usage},
        'non_unique_error_code_fixtures': fixtures,
        'isolated_temporary_ledger_stop_fixture': guard,
        'original_ledger_modified': False,
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
