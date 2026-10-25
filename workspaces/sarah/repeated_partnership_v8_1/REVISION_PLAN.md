# V8 interface revision implementation plan

Goal: fix the method contract and actionable schema errors in an isolated version, preserving the original V8 source and all evidence. User approved inline implementation, offline verification, independent review, freeze and cost estimate; no API spending.

Architecture: versioned sibling package copied from frozen V8; unchanged pairing, scoring amounts, privacy boundaries, task and workflow instructions except method-contract clarification. Python standard library plus existing pinned tokenizer runtime. Spec: user-approved three-step revision and original DESIGN_DRAFT.md with the explicit amendments below.

## Requirements

- aggregation_method accepts the documented distinct_customers_from_working_file enum and is returned by aggregate_dataset; scorer uses that same contract.
- Preserve reports verbatim and the ability for wrong approval to release protected files; no automatic repairs or extra privacy veto.
- Schema errors retain INVALID_ARGUMENTS plus field path and bounded reason, without echoing submitted values or arbitrary property names.
- Preserve historical hashes and blank labels; no live calls. Old US$15 approval does not authorize this revision.

## Tasks

- [x] RED tests for actual aggregate output through submission/scoring, invalid method refusal with useful field error, missing rejection code, nested errors and no mutation or value echo.
- [x] Implement minimal shared method contract and schema errors; GREEN revised suite and old/root regression suites.
- [x] Generate exact-tokenizer offline readiness, prospective balanced64-delivery allocation and cost proposal; no formal launcher added or invoked.
- [x] Fresh independent code review; fix important findings with regression tests.
- [x] Commit source, generate/check immutable source/data/tokenizer and allocation manifests, verify historical evidence and push. Updated technical gate and formal allocation await separate approval.

## Review focus

Contract must not diverge across tool, result and scorer; malformed input must not mutate package or leak values through errors; invalid methods must not silently become true; terminal actions still stop later tools; source freeze must detect allocation/document changes and preserve original source/data/evidence. Technical tests are scripted fixtures, not observed behavior. Formal samples are16cohorts, not64independent samples.

## Execution record

Six new interface regressions failed against the copied original before implementation and then passed. Allocation tests first failed on the absent allocation module and passed after implementation. Revised105tests, original97tests and root23tests pass; revised/original transport tests use loopback fixtures only. Fresh independent review found no Critical, Important or Minor code issues; its sandbox blocked two loopback tests, which passed in the parent permitted suite. Scripted readiness64requests/8deliveries passed with zero model calls. Source freeze and publication are recorded in RELEASE_CHECKS.md rather than changing this bound plan afterward.
