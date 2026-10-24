# Financial intermediate-file v7 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compare three financial delivery workflows with matched cleanup control and optional private channel.
**Architecture:** New self-contained actor copied from frozen v6, multi-file append/explicit cleanup, actual file-driven aggregation, immutable logs and package hash. Separate fixed collector/advisory audit/results, no edits to prior actors or evidence.
**Tech Stack:** Python3 standard library, SQLite, existing bounded OpenAI-compatible client.
**Spec:** workspaces/sarah/intermediate_workflow_v7/PROTOCOL.md

## Global Constraints

Sarah-only branch/directory. No Julien/shared-branch changes.30new episodes maximum:6smoke+24formal.16requests/episode,8/role,4096completiontokens/request,90s timeout, exactmodel gpt-5-mini-2025-08-07. Same v4 syntheticdata/license/P1 acrosssixcells. Local releases only; no privacy veto on wrongapproval. Source/config pushed before calls. Humanblank/rawunreviewed. Prior evidence immutable.

## Review Focus

- Mixed package: approval must release every file despite aggregate claim; test real20kraw release and report unchanged.
- Wrong filename, empty file/candidate, invalid offset: clear tool errors without mutation.
- Cleanup/lock: removing work before computation cannot silently aggregate from DB; removal afterlock impossible; sources/logs unchanged.
- Whole-package identity: insertion order neutral, removing/replacing file changes hash, onefilehash cannot approve mixedpackage.
- Role/history: audit operationalonly, citation ownership checked, private messages recipientonly, failure/checkpoint preservation.

### Task1: Multi-file actor and executable paths

Files: create runner.py, test_workflow.py in this directory. Consumes frozen v6 behavior/client; produces _Environment, _tools_for, run_live_episode, CONDITIONS, configuration. Use filename string inspection and package_sha256 decision argument. W1 distinct-customer count from working raw; W2 sum20buckets; W0 direct. Working/aggregate/raw-export changes upsert named files; explicit removal.

- [ ] Write failing unittest cases for sixcells, W1/W2 require materialization, correct file-driven count and retention, precomputation removal error, safe cleanup/approval, mixedrelease, named inspection and malformed inputs, hash identity/citations, locked immutability, channel/audit separation.
- [ ] Run python3 -m unittest discover -s workspaces/sarah/intermediate_workflow_v7 -p test_workflow.py -q; expect missing runner or old incompatible behavior.
- [ ] Implement new runner APIs per protocol without editing frozen v6.
- [ ] Run same tests; expect all pass; run root tests23; commit verified actor.

### Task2: Fixed collection and evidence checks

Files: create collect.py, test_collection.py; later audit_evidence.py/export_review.py. Consumes Task1 configuration/rows; produces exclusive frozen manifest6/24allocation, durable raw checkpoints, mechanical summary and blank human file. Seed2026102503, six-cell blocks. Freeze new actor/tests/protocol/plan plus imports/data and every prior completed evidence hash. Check prior v6source/evidence unchanged. Summaries distinguish internal rawworkingfile, optionalrawexport, rawsubmission/release, useful final package, safe extra files.

- [ ] Test fixed schedule/cell counts; malformed providerresponse stops after preserved slot; interruptedslot refuses rerun; raw release validates actual eachfile against source.
- [ ] Observe failure, implement collector, rerun tests; expect allpass.
- [ ] Run full new/root suites, fresh whole-source reviewer, resolve material findings with red→green tests. Freeze/push source/config before first call.

### Task3: Smoke, formal, raw review, report and delivery

- [ ] Collect six smoke once, preserve all. Verify frozen/source/priorhashes, per-roletool/history/recipienttransport, actual multi-file contents/hash and decisionrefs. Raw-first independent review; gate beforeformal.
- [ ] Collect fixed24formal; push preserved checkpoints, no substitutes or selection. Review every rawepisode before summary; independent crosscheck cites episode/global seq.
- [ ] Export advisory AIreview and blank humanlabels, English/Chinese reports, evidenceZIP without secrets. Separate uncertainty, workflowutility/privacy/reporterrors/coordination. Verify tests and hashes, push Sarahbranch, update handoff/ledger. Do not pool oldcohorts or infer generalrates.

Self-review: protocol maps to Tasks1–3; allfive ReviewFocus cases covered Task1/2; collector imports and exact condition suffixes align. Inline autonomous execution already authorized by user; no new confirmation needed.
