"""Offline two-round orchestration. No providers, retries or API entry point."""
from copy import deepcopy
import hashlib
from pathlib import Path

from .adapter import TaskAdapter, memory_from_journal
from .cohort import Cohort, ACTORS
from .scoring import load_source


class CohortAdapter:
    def __init__(self,journal,dataset,*,execution_order=None):
        self.journal=journal;self.dataset=Path(dataset)
        self.source=load_source(dataset)
        self.dataset_sha256=hashlib.sha256(self.dataset.read_bytes()).hexdigest()
        context=journal.context()
        self.cohort_id=context['cohort_id'];self.condition=context['condition']
        tasks=journal.db.execute('SELECT request_id,round_index,preparer FROM tasks ORDER BY round_index,preparer').fetchall()
        order=deepcopy(execution_order)if execution_order is not None else [t['request_id']for t in tasks]
        journal.bind_schedule(self.dataset_sha256,order)
        self.order=order
        self.poisoned=False

    def _check(self):
        if self.poisoned:raise ValueError('Coordinator stopped; explicit recovery required')
        if hashlib.sha256(self.dataset.read_bytes()).hexdigest()!=self.dataset_sha256:
            self.poisoned=True
            raise ValueError('Bound source changed')

    def start_next(self):
        self._check()
        snapshots=[self.journal.snapshot(request)for request in self.order]
        if any(s['state']=='running'for s in snapshots):
            raise ValueError('Active/uncertain task; no rerun')
        if any(s['terminal']=='api_failure'for s in snapshots):
            raise ValueError('Cohort stopped by API failure')
        pending=next((s for s in snapshots if s['state']=='pending'),None)
        if pending is None:
            self.complete_round(2)
            return None
        if pending['round_index']==2:self.complete_round(1)
        return TaskAdapter(self.journal,pending['request_id'],self.dataset)

    def complete_round(self,round_index):
        self._check()
        existing=self.journal.barrier(round_index)
        if existing is not None:return existing
        snapshots=[self.journal.snapshot(request)for request in self.order]
        current=[s for s in snapshots if s['round_index']==round_index]
        if len(current)!=2 or any(s['state']!='terminal'for s in current):
            raise ValueError('Both round deliveries must terminate before feedback')
        if round_index==2 and self.journal.barrier(1)is None:
            raise ValueError('Prior barrier missing')
        cohort=Cohort(self.condition,self.cohort_id)
        for s in snapshots:
            if s['round_index']<=round_index:
                if s['state']!='terminal':raise ValueError('Earlier round incomplete')
                cohort.finish(s['round_index'],s['preparer'],s['terminal'],s['points'])
        public=cohort.feedback(round_index,'P1')
        actors={}
        for actor in ACTORS:
            own=next(s for s in current if actor in (s['preparer'],s['reviewer']))
            terminal_event=next(e for e in self.journal.events()if e['request_id']==own['request_id']and e['kind']=='terminal')
            actors[actor]={'memory':memory_from_journal(self.journal,own['request_id'],actor,self.source),
                           'own_terminal_feedback':{'request_id':own['request_id'],'terminal':own['terminal'],
                                                    'source_event_id':terminal_event['event_id'],'exposure':'new_at_round_barrier'},
                           'public_feedback':deepcopy(public)}
        payload={'round_index':round_index,'public_feedback':public,'actors':actors}
        try:
            return self.journal.publish_barrier(round_index,payload)
        except BaseException:
            self.poisoned=True
            raise
