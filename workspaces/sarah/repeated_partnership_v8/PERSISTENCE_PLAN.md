# V8 durable journal phase

Offline implementation under Sarah's continuing authorization. No API calls, source freeze or allocation approval. Existing dedicated Sarah checkout on sarah/pilot-run is reused. Binding design: DESIGN_DRAFT.md Appendix A2/A4. Follow executing-plans and TDD.

## Scope and contracts

Create journal.py and test_journal.py. One exclusive SQLite database per cohort, four predeclared unique task IDs (round1 P1/P2, round2 P1/P2), condition and configuration SHA256 pinned at creation. Database permissions0600. No provider imports. Journal accepts trusted adapter/scorer records, not model claims; it does not implement semantic evaluation or a buyer transport.

Tasks transition pending -> running -> terminal once only. Claim is durable before future external calls. Reopening a running task never permits automatic rerun. Round2 claims require both round1 terminals and no api_failure; otherwise fail closed. Host uncertainty remains running and requires explicit future recovery, not guessed feedback. Event IDs are cohort-local0..4095. Appends/terminals serialized via BEGIN IMMEDIATE. Terminal snapshot (files, report, tool result, points) and terminal event commit in a single SQLite transaction. Approval has a nonempty released file snapshot; other terminals must not carry released files. Existing terminal cannot be replaced by later timeout/failure. No exporting to an external buyer yet.

## Tasks

- [x] Write failing tests for exclusive creation, metadata/reopen validation, four slots, role pairing, round barrier, duplicate/concurrent claims, no interrupted rerun, event sequence/cross-task ownership, atomic terminal rollback, exact approved snapshot after reopen, no nonapproval release, late failure preservation, explicit api_failure blocks round2, invalid/non-JSON input leaves state unchanged.
- [x] Implement minimal SQLite journal; run persistence tests GREEN.
- [x] Run full V8, root and frozenV7 suites; verify24V7source hashes unchanged and Sarah-only changes.
- [x] Fresh final code review; fix important findings with RED->GREEN regressions. Update status/ledger and push only sarah/pilot-run.

Review focus: transaction rollback and concurrent connections; uncertain running state; wrong identities/config; release snapshot vs terminal consistency; event bounds and malformed inputs. Excluded: actual provider input/visibility construction, scorer correctness (separate existing subsystem), live cost/token gate, collector/recovery implementation. This journal is not the full V8 runner.

## Completion evidence

9 journal tests / 29 total V8 tests pass; root23 and frozenV7 21 pass. Fresh independent review found one Important mutable-input/transaction-lock race, reproduced by a failing regression and fixed by a detached single JSON snapshot shared by the task row and terminal event. No Critical findings. Deferred test gaps: simultaneous contention stress, event-cap exhaustion and invalid initialization matrix. Second-connection coverage is sequential, not simultaneous stress. These gaps remain before live collection readiness.
