# V8 two-round coordinator — offline implementation plan

User authorized next step after182d246. Reuse dedicated Sarah checkout/sarah/pilot-run. Execute inline with TDD and one fresh final review, following writing-plans/executing-plans. Binding spec DESIGN_DRAFT.md §§3–6, A2/A4. No model/API/paid execution, allocation or source freeze.

## Architecture

Create coordinator.py/test_coordinator.py. CohortAdapter binds a source SHA256 and four-task counterbalanced order before any task claim, exposes start_next() for one active TaskAdapter, and complete_round(round_index) for durable feedback. Journal gains version2 coordination records and schedule/barrier validation. Old version1 journals are not silently migrated/resumed. No existing experiment journal is changed; only temp test databases are created. A bound schedule may not be rebound or automatically resumed by constructing another coordinator.

TaskAdapter retains round1 standalone testing. Round2 requires a durable round1 barrier produced by the coordinator; histories are fresh with only actor-specific prior memory, own terminal feedback, public whitelist and explicit correct partner notice. No entire cohort barrier/raw peer trace is exposed. Existing current-task consumption sets start empty; prior round evidence IDs are context only and cannot authorize current decisions. Source hash must match schedule binding.

## Interfaces and invariants

- Journal.bind_schedule(dataset_sha256, execution_order): validate exact four request IDs in two round blocks, all pending, exclusive binding, serialized transaction. Claim enforces bound order. Context/version and bound SHA256 remain pinned.
- Journal.publish_barrier(round_index,payload): trusted coordinator payload, no external/model interface. Two matching terminal slots required, prior barrier for round2; durable feedback event and coordination record in one transaction; no duplicates/guessed output. Payload detached before lock wait. Journal.barrier and schedule return decoded copies.
- CohortAdapter(journal,dataset,execution_order=None): validates source/readiness then binds once. start_next refuses active/uncertain slots; automatically requires/publishes round1 barrier before round2. After all4terminal, complete_round(2) records final feedback without extra model inputs.
- complete_round derives outcomes/points from committed journal snapshots, hydrates existing Cohort, extracts each actor's own prior memory from raw actual-input provenance, builds fixed own terminal feedback + actor-unlabeled public count block (+team totals F1only). Memory terminal exposure is not rewritten; new feedback deliberately supplies terminal information at the barrier. Feedback preparation is not model consumption; round2 actual inputs log exposure.
- TaskAdapter memory extraction factored as memory_from_journal, same filtering/redaction. Constructor validates stored actor scope and uses correct stable/exchanged partner notice, not the old unconditional 'no'. Only selected actor block enters its input.

## Tasks

- [x] RED tests: four conditions/two rounds with persistent actors; both prior finals required; fresh histories/own-only memory/partner notice; F0no numeric/F1samecohort totals; source/order binding immutable; other pair/private/row exclusion and correct previous partner; prior-reference rejection; final feedback no extra requests; interruption/poison stops continuation; source change rejected; atomic feedback rollback; invalid schedule and premature publication rejected.
- [x] Implement coordinator + minimal journal/adapter integration; no provider imports.
- [x] Full V8/root/frozenV7 tests,24V7raw hashes and Sarah-only diff.
- [x] Fresh review and one failing-regression fix pass for material findings; document residual limits, commit/push.

Review focus: no barrier exposure before both tasks terminate, exact assigned actor carryover, pairing/feedback field whitelist, source/order identity, atomic publication/reopening, old reference rejection, partial/missing/no-decision preservation. Provider parsing, timeout distinction, exact tokenizer/cost, explicit recovery, collector and live freeze remain outside this phase. Earlier journal stress/event-cap/init test gaps remain pending live-readiness work.

## Completion gate

12coordinator tests /59V8total, root23 and frozenV7 21 pass. All24V7raw hashes unchanged. Fresh independent read-only review found no Critical/Important issues. No claim provider/live readiness. Deferred new test gaps: every reviewer's carryover/prior-partner assertions across allfourcells; abort during coordination-row insert after feedback-event insertion; distinct per-round scores in cumulative-final-total assertion. Previously deferred journal stress/event-cap/init coverage remains.
