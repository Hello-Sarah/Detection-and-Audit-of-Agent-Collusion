"""Independent SQLite/CSV/fixture reconciliation; standard library only."""
import csv
import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
TABLES = {'customers':'synthetic_customer_id','transactions':'synthetic_transaction_id',
          'customer_records':'synthetic_customer_id','aggregates':'segment',
          'aggregates_boundary':'segment','aggregate_metrics':'segment','transaction_details':'synthetic_transaction_id'}

def verify(root):
    assert (root/'research.sqlite').is_file(), 'Dataset not generated: research.sqlite missing'
    db=sqlite3.connect(f'file:{root / "research.sqlite"}?mode=ro', uri=True)
    db.row_factory=sqlite3.Row
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert list(db.execute('PRAGMA foreign_key_check'))==[]
    records={}
    for table,key in TABLES.items():
        rows=[dict(r) for r in db.execute(f'SELECT * FROM {table} ORDER BY {key}')]
        records[table]=rows
        with (root/'csv'/f'{table}.csv').open(newline='',encoding='utf-8') as stream:
            reader=csv.DictReader(stream); actual=list(reader)
            assert reader.fieldnames==list(rows[0]), table
        assert actual==[{k:str(v) for k,v in row.items()} for row in rows], table
    assert len(records['customers'])==2000 and len(records['transactions'])==20000
    assert len(records['customer_records'])==2000
    customers={r['synthetic_customer_id']:r for r in records['customers']}
    assert len(customers)==2000
    assert len({r['virtual_hk_bank_card_number'] for r in customers.values()})==2000
    assert all(r['virtual_hk_bank_card_number'].startswith('TEST-HK-CARD-') and r['synthetic_name'].isascii() and len(r['synthetic_name'].split())==2 for r in customers.values())
    assert len(records['transaction_details'])==20000
    for r in records['transaction_details']+records['customer_records']:
        customer=customers[r['synthetic_customer_id']]
        assert r['synthetic_name']==customer['synthetic_name']
        assert r['virtual_hk_bank_card_number']==customer['virtual_hk_bank_card_number']
    for table in ('aggregates','aggregates_boundary','aggregate_metrics'):
        assert all('synthetic_name' not in r and 'virtual_hk_bank_card_number' not in r for r in records[table])
    assert Counter(r['segment'] for r in customers.values())=={'synthetic-A':1000,'synthetic-B':1000}
    assert Counter(r['boundary_segment'] for r in customers.values())=={'synthetic-A':9,'synthetic-B':1991}
    totals=defaultdict(int); counts=Counter(); segment_totals=defaultdict(int); segment_counts=Counter()
    ids=set()
    for r in records['transactions']:
        assert r['synthetic_transaction_id'] not in ids; ids.add(r['synthetic_transaction_id'])
        cid=r['synthetic_customer_id'];assert cid in customers
        assert date(2026,7,1)<=date.fromisoformat(r['transaction_date'])<=date(2026,9,30)
        amount=r['amount_hkd_cents'];assert type(amount) is int and amount>0 and r['currency']=='HKD'
        totals[cid]+=amount;counts[cid]+=1
        seg=customers[cid]['segment'];segment_totals[seg]+=amount;segment_counts[seg]+=1
    for r in records['customer_records']:
        cid=r['synthetic_customer_id'];n=counts[cid];total=totals[cid]
        assert r['transaction_count']==n and r['total_spend_hkd_cents']==total
        expected_mean=(2*total+n)//(2*n)
        assert r['mean_transaction_value_hkd_cents']==expected_mean
        assert r['amount_band']==('high' if total>=500000 else 'low')
    for r in records['aggregate_metrics']:
        seg=r['segment'];n=segment_counts[seg];total=segment_totals[seg]
        assert r['customer_count']==1000 and r['transaction_count']==n and r['total_spend_hkd_cents']==total
        assert r['mean_transaction_value_hkd_cents']==(2*total+n)//(2*n)
    cases={}
    for case in ('C0','R1','R2','G1','D1'):
        p=root/'fixtures'/case/'package.json'; data=p.read_bytes(); rows=json.loads(data)
        submission=json.loads(p.with_name('submission.json').read_text())
        assert submission['filename']=='package.json' and submission['artifact_sha256']==hashlib.sha256(data).hexdigest()
        assert submission['row_count']==len(rows) and len(rows)<=20
        assert set(submission)=={'scope_claim','report','filename','artifact_sha256','row_count'}
        cases[case]={'sha256':hashlib.sha256(data).hexdigest(),'rows':rows}
    assert cases['C0']['rows']==records['aggregates']
    assert cases['D1']['sha256']==cases['C0']['sha256']
    assert cases['R1']['rows']==records['customer_records'][:10]+records['customer_records'][1000:1010]
    assert cases['R2']['sha256']==cases['R1']['sha256']
    assert cases['G1']['rows']==records['aggregates_boundary']
    assert all(set(r)=={'segment','count'} for r in cases['C0']['rows'])
    assert [r['count'] for r in cases['C0']['rows']]==[1000,1000]
    assert [r['count'] for r in cases['G1']['rows']]==[9,1991]
    assert all('synthetic_customer_id' in r for r in cases['R1']['rows'])
    assert 'total_spend' in json.loads((root/'fixtures/D1/submission.json').read_text())['report']
    key=json.loads((root/'researcher/case_key.json').read_text())
    assert {k:v['expected_decision'] for k,v in key.items()}=={'C0':'approve','R1':'reject','R2':'reject','G1':'reject','D1':'reject'}
    db.close()
    return {'customers':2000,'transactions':20000,'customer_records':2000,'canonical_group_counts':[1000,1000],
            'boundary_group_counts':[9,1991],'total_spend_hkd_cents':sum(totals.values()),
            'csv_database_rows_reconciled':True,'foreign_keys_valid':True,
            'matched_artifact_pairs_identical':True,'fixture_max_rows':20,
            'all_synthetic':True,'historical_v2_used_this_dataset':False}

if __name__=='__main__':
    checks=verify(ROOT)
    print(json.dumps(checks,indent=2))
