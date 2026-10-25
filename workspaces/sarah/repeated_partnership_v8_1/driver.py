"""Two-round protocol/budget integration. Explicit transport, no automatic resume."""
import hashlib
import json
from pathlib import Path
import sqlite3
from .budget import BoundedDispatcher,BudgetStop
from .protocol import build_request,serialized_token_estimate


class RunStopped(RuntimeError):pass


class Driver:
    def __init__(self,coordinator,ledger,transport,*,estimator=serialized_token_estimate,guard=None):
        self.coordinator=coordinator;self.ledger=ledger;self.transport=transport
        self.estimator=estimator;self.guard=guard;self.stopped=False

    def step(self,task):
        if self.stopped or task.terminal:raise RunStopped('RUN_STOPPED_OR_TERMINAL')
        actor=task.actors[task.turn%2]
        predispatch_failed=False
        try:
            if self.guard is not None:self.guard()
            packet=task.input(actor,dispatched=False)
            prepared=build_request(packet)
            estimate=self.estimator(prepared)
            count=estimate.get('serialized_body_tokens')
            if type(count)is not int or not 0<count<=200000:raise RunStopped('INPUT_TOKEN_PREFLIGHT_FAILED')
            call_id='v8_'+hashlib.sha256((task.cohort_id+':'+task.request_id+':'+str(task._pending_input['event_id'])).encode()).hexdigest()
            task._log('api_attempt',actor=actor,call_id=call_id,payload_sha256=prepared.sha256,token_estimate=estimate)
            def transport(body,timeout):
                nonlocal predispatch_failed
                try:
                    if hashlib.sha256(body).hexdigest()!=prepared.sha256:raise RuntimeError('REQUEST_DIGEST_MISMATCH')
                    if self.guard is not None:self.guard()
                    task.mark_dispatched(actor,call_id,prepared.sha256)
                except BaseException:
                    predispatch_failed=True
                    raise
                return self.transport(body,timeout)
            parsed=BoundedDispatcher(self.ledger,transport).dispatch(call_id,packet)
            return task.respond_provider(actor,parsed.raw,call_id)
        except BudgetStop as exc:
            self.stopped=True
            code=str(exc)
            if predispatch_failed:raise RunStopped('PRE_DISPATCH_INTEGRITY_FAILURE')from None
            if code in ('TIMEOUT','TRANSPORT_ERROR','INVALID_RESPONSE','ACCOUNTING_ERROR','INTERRUPTED'):
                task.fail_api(code)
            else:
                task._log('error',actor='harness',error='BUDGET_STOP_BEFORE_DISPATCH')
            raise RunStopped(code)from None
        except BaseException:
            self.stopped=True
            raise

    def run(self):
        if self.stopped:raise RunStopped('RUN_STOPPED')
        try:
            while True:
                task=self.coordinator.start_next()
                if task is None:return
                while not task.terminal:self.step(task)
        except BaseException:
            self.stopped=True
            raise


def recovery_report(path):
    """Read-only inventory. Does not infer a score, mutate or resume any slot."""
    db=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        tasks=[dict(r)for r in db.execute('SELECT request_id,state,terminal,points FROM tasks ORDER BY round_index,preparer')]
        return {'automatic_resume_allowed':False,'running_requests':[r['request_id']for r in tasks if r['state']=='running'],
                'pending_requests':[r['request_id']for r in tasks if r['state']=='pending'],
                'terminal_records':[r for r in tasks if r['state']=='terminal'],
                'instruction':'Preserve journals and budget holds; explicit reconstruction/approval required. Never rerun a claimed slot.'}
    finally:db.close()
