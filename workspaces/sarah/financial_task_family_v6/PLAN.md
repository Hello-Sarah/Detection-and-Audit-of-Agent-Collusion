# Financial task-family v6 Implementation Plan

> For agentic workers: use superpowers:executing-plans inline; one fresh whole-source reviewer before freeze.

Goal: compare four business tasks within Sarah's financial release scenario using an unchanged evidence standard.
Architecture: copy the frozen v5 runner and collector into this new Sarah module; add task request selection to explicit condition configuration. Never mutate frozen v5 modules or use global monkey-patching. Preserve the v5 environment and independent role histories.
Tech stack: Python standard library, existing read-only SQLite, existing OpenAI-compatible client.
Spec: workspaces/sarah/financial_task_family_v6/PROTOCOL.md

## Global constraints
sarah/* only; fictional v4 English source; 8 smoke +32 formal maximum; model gpt-5-mini-2025-08-07;16 alternating requests/8 per role;4096 completion tokens;90seconds;all raw labels unreviewed and human labels null. No outcome-dependent expansion, no old source changes.

## Review focus
- Task code changes must not leak channel messages through common state/audit.
- Full raw release must remain possible despite a false aggregate claim.
- Task identity/configuration and actual API input must agree in all eight cells.
- Frozen hashes must cover new source and all old evidence, with separate denominators.
- API/protocol failure and interruption must preserve the allocated slot and stop safely.

### Task1: task-aware runner
Files: new runner.py, test_tasks.py and copied v5 behavioral tests in this folder.
Interface: CONDITIONS uses N0P1T0 through N1P1T3; buyer_request(condition) selects task objective; run_live_episode retains explicit condition, request, source and dataset configuration.
- [ ] Write tests for eight cells and matched request/channel/pressure behavior; watch failure against unchanged v5 copy.
- [ ] Add task bank/selection; retain all existing environment safeguards and permissive wrong-approval mechanics.
- [ ] Run tests including role isolation, raw release, terminal hold, malformed response preservation, fixed rounds and actual request token cap.
- [ ] Commit source stage.

### Task2: frozen collection
Files: collect.py, test_collection.py, test_tasks.py.
Interface: schedule(smoke=False) yields8or32slots in blocks of8; freeze() records all source/data/historical digests and exact configs; collect(folder) preserves failures/checkpoints without replacement; summarize(folder) only mechanical facts.
- [ ] Write schedule and failure preservation tests; watch failure before implementation.
- [ ] Adapt collector with seed2026102502, new folders and v5 prior gate; freeze includes all new tests/protocol/plan.
- [ ] Run new suite and repository suite; independent whole-source review; fix substantial findings with red→green tests.
- [ ] Freeze, commit and push before live requests.

### Task3: smoke, bounded formal collection and evidence review
Files: new2026-10-25financial_task_v6_smoke_01andfinancial_task_v6_01runfolders; separate AI review and results documents.
- [ ] Run8smoke, review raw mechanics and source/config integrity; preserve all outcomes.
- [ ] If technical gate passes, collect32formal under unchanged source with checkpoint pushes.
- [ ] Inspect all raw traces before summary comparison; separate safety, report integrity, utility and coordination with episode/seq references.
- [ ] Keep human worksheet blank; publish bounded English/Chinese reports and evidence export; update Sarah index/handoff; push final stage.
