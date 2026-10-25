"""Prospective allocation and cost proposal only; no client or run command."""
from decimal import Decimal
import random
from .budget import RESERVE_NUSD
from .cohort import CONDITIONS

SEED=2026102504

def formal_allocation():
    rng=random.Random(SEED)
    orders={}
    for condition in CONDITIONS:
        choices=[(False,False),(False,True),(True,False),(True,True)]
        rng.shuffle(choices);orders[condition]=choices
    cohorts=[]
    for block in range(1,5):
        conditions=list(CONDITIONS);rng.shuffle(conditions)
        for condition in conditions:
            cohort=f'v8r1formal_b{block}_{condition.lower()}'
            ids=[cohort+'_'+suffix for suffix in ('a','b','c','d')]
            first,second=orders[condition][block-1]
            sequence=([1,0]if first else[0,1])+([3,2]if second else[2,3])
            cohorts.append({'block':block,'cohort_id':cohort,'condition':condition,'request_ids':ids,
                            'execution_order':[ids[i]for i in sequence]})
    return cohorts

def cost_proposal():
    amount=lambda n:str(Decimal(n*RESERVE_NUSD)/Decimal(10**9))
    return {'spending_authorized':False,'formal_deliveries':64,'independent_formal_cohorts':16,
            'formal_requests_max':1024,'technical_deliveries':8,'technical_requests_max':128,
            'formal_uncached_ceiling_usd':amount(1024),'technical_uncached_ceiling_usd':amount(128),
            'combined_uncached_ceiling_usd':amount(1152),
            'proposed_formal_cap_usd':'115','proposed_technical_cap_usd':'15',
            'note':'Conservative token reservations, not expected bills. Historical approval is not transferable. No formal launcher is supplied by this allocation module.'}
