# Controlled invitation collector implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline; one fresh read-only final reviewer before execution freeze.

**Goal:** Prepare and freeze the16-slot reviewer-only API collector without making paid calls.

**Architecture:** Keep engine.py and the frozen V8.1 dependency unchanged. Add collector.py to validate a separately prepared immutable bundle, use one conservative budget ledger and persistent transport for the entire allocation, and export exact inputs/responses, artifacts, failure/unknown/unrun records and blank review fields. No retry/resume/replacement. User approved offline construction, review and freezing only; proposed US$8 collection requires separate explicit approval.

**Tech stack:** Existing pinned Python3.14/tiktoken0.12.0, SQLite journals, existing Driver/BudgetLedger and DiagnosticTransport/PersistentTransport. Official Chat Completions endpoint only. Existing four conditions and random seed remain unchanged.

- [x] Task1: Write failing end-to-end tests for16fresh contexts, same stimulus checks, global stop on transport/invalid response/integrity failure, missing/unrun/unknown denominators, artifact exports, cap and approval/exclusive output checks. Then implement collector.py and pass tests.
- [x] Task2: Add failing freeze/tamper and pre-dispatch request hash tests; prepare/check execution bundle. All16 first request bodies, reports/packages/messages, source/data/tokenizer/rates and allocation are bound. Do not modify prior offline_proposal_01 or old evidence. Export every actual request body and preserved provider response, whole local release contents, journal trace, score caveat, and hashes; human fields blank.
- [x] Task3: Full relevant regressions, fresh independent review, resolve material findings via RED→GREEN, historical hash checks. Update English/Chinese README. Commit source, generate execution_freeze_01 (status frozen_pending_approval), verify, commit freeze and push sarah/pilot-run. No paid dispatch, no old-run restart.

Evidence contract: initial exposure means confirmed provider-response/input linkage, not merely a dispatch. Terminal decisions include only executed approved/rejected/held outcomes; limit/failure are separate. Safety observations use actual released rows. Unrun, failed-before-response and confirmed-but-nonterminal cases remain distinct. Do not auto-label verbal acceptance, false rationale, collusion or intent; human annotations remain null. Current legacy mechanical reference_remove error for deliberately retained working files is not a semantic false-report label.

Budget contract: one64-request ledger, US$8 cap, conservative per-call hold US$0.108192 under pinned provisional rates; fail closed before any send if pricing/runtime/config/approval cannot be validated. Never release uncertain holds automatically. A stopped or existing directory cannot resume; export checkpoints after episodes without overwriting original journals or provider evidence. Frozen artifacts confer no spending approval.


## Implementation and final review ledger

Task1: five missing-feature tests RED, collector implemented, first five GREEN. Two injected initialization/export failures then reproduced incorrect missingness (RED); preserving an initialized failure and capturing a journal outcome before export made both GREEN. Global budget is stopped on every batch failure. Expanded10-test suite passed before final review.

Task2: one-shot claim test RED→GREEN. Added exact initial-body tamper,64-request limit, preflight, second-slot failure, interruption, artifact-hash, approval/cap and stale-pricing checks. Full34new/current integration tests,116frozen dependency/transport regressions and23root tests passed before final review.

Final review: fresh read-only reviewer passed14focused tests; no Critical/Important findings. Its checkpoint-state finding was regraded Important here because a machine-readable completed flag could incorrectly admit a partial allocation to downstream completion checks. Fixed via test_progress.test_only_fully_resolved_allocation_is_completed RED→GREEN; final suite rerun recorded in COLLECTOR_VERIFICATION.json.

Final: Ruling: live model behavior, account access, actual billing and empirical collusion remain unjudged. The current approval covers offline preparation only, so no model request or credential check is made; the possible cost is an unavailable model or failed first call after later authorization, with conservative cost hold retained and batch stopped. These are not passed gates or observed model findings.

No deferred code-review minor findings. Physical disk/process failure may leave partial exports and a one-shot claim; preserve evidence/holds for manual investigation and never auto-resume.

Final verification:35current collector/engine/integration tests passed after the checkpoint fix;116unchanged frozen dependency/transport regressions and23root tests passed. The execution bundle and its final hash checks are recorded separately in COLLECTOR_VERIFICATION.json; no paid run is part of this plan.
