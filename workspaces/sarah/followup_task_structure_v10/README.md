# V10 task-structure diagnostic

V10 is a bounded, 24-episode exploratory study of how a model reviewer handles synthetic customer-linked data in two financial tasks after receiving one of three scripted messages. The conditions cross transaction reconciliation or customer-feature preparation with a neutral handoff, false compliance assurance, or an explicit request to make an exception and misstate the package.

Only the reviewer is a model; the preparer is a disclosed script. This diagnoses responses to prompted behavior. It cannot estimate spontaneous two-model collusion or rank task types generally. All data are synthetic. No human or semantic label is filled by the runner.

The frozen design, evidence coding rules, source, allocation and exact initial requests live in this directory. Actual per-episode trajectories and released files will be stored under `workspaces/sarah/experiment_runs/2026-10-26/task_structure_v10_01/`.

Before live execution, `collector.py prepare` creates an offline-only package. After the package is committed and pushed, a live run can use:

```sh
../v8-runtime/bin/python -m workspaces.sarah.followup_task_structure_v10.collector run \
  --manifest workspaces/sarah/followup_task_structure_v10/execution_freeze_01/EXECUTION_MANIFEST.json \
  --output workspaces/sarah/experiment_runs/2026-10-26/task_structure_v10_01 \
  --approval-ref user-approved-v10-24-us10-shared \
  --cap-usd 9.756574
```

The extension shares the earlier V9 US$10 total ceiling. Its ledger is capped at the remaining US$9.756574 and checks the V9 ledger hash and settled accounting on each dispatch. It stops on budget refusal, uncertain transport, invalid response accounting, or integrity failure; no retry, resume, replacement, or additional episode is automatic. Pricing snapshots are estimates, not invoices.
