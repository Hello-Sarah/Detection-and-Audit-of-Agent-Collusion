# V8 technical-run integration and readiness

User asked next step and why no paid calls after0555314. Complete a concrete technical-run package before asking for cap/allocation approval. Existing Sarah checkout/sarah/pilot-run. Inline TDD + fresh final review. No paid calls in this phase.

## Scope

Integrate protocol/budget with TaskAdapter/CohortAdapter. Add real official-endpoint HTTP transport (no invocation here), exact snapshot tokenizer dependency in separate ignored/outside-repo runtime, offline calibration/readiness record, fail-closed interrupted-journal report and frozen technical manifest. No automatic resumed/replaced task. Human approval/cap remains final live gate; formal allocation not authorized.

Two-stage input provenance: input(dispatched=False) records input_prepared only; reserve before transport; mark_dispatched logs actual api_input with confirmation_required and a unique budget call ID. Valid raw provider response confirms that input for memory/private receipt/scoring; timeout/malformed/no-send never invents confirmed observations. Scripted input default remains explicitly confirmed for existing fixtures. Driver checks exact request digest, records raw response and original tool IDs, replays original assistant calls/results with matching IDs, and never executes truncated/refusal calls. Ordinary malformed generated arguments receive bounded tool error, not repaired facts.

Provider failure before any applied tools records api_failure(reason code), no raw release; systemic uncertainty stops allocation. Existing terminal outcomes cannot be replaced by later errors. Budget refusal before dispatch preserves partial/unrun states and no invented score. Cross-database failure leaves evidence and cost holds for explicit inspection, never automatic replay. Add read-only recovery report, not a mutating resume command.

Transport: fixed https://api.openai.com/v1/chat/completions only,90seconds, no redirects/retries, no credentials in journals/exception text. Key read only inside explicit live setup after readiness+human cap gate; current phase only validates key presence safely. Transport tested against a loopback fake HTTP server, never OpenAI.

Token preflight: tiktoken0.12.0 exact model o200k_base; measure complete serialized inputs/tools (including carryover) without special-token rejection. Local count is not exact hidden provider formatting. Proposed common200000serialized-token guard plus400000input worst-case billing reserve; no truncation. First approved technical responses compare observed usage to local estimates within the same8deliveries, no extra calibration calls. Price/model caps from official docs fetched previous phase, reverify at actual launch.

Technical proposal:2cohorts S1F1/S0F0 ×4deliveries=8, at most128requests,4096completion each, cap proposalUSD15 (conservative max128×0.108192=13.848576). All delivery outcomes retained; mechanical gate only, no outcome chasing. No formal64deliveries automatically follows. Manifest pins source/data/config/tokenizer and counterbalanced order before any live call; publish freeze only after final review. CLI must refuse absent explicit approval-ref and cap, stale hashes/tokenizer, preexisting run files or nonofficial base. No production budget/journal created until approval.

## Tasks

- [x] RED integration tests for original call IDs/raw malformed args, complete scripted two-round provider flow, truncated/refusal history validity, denied/timeout/unconfirmed provenance, terminal-before-later-call behavior, actual request digest/budget linkage, no repeated failed calls.
- [x] Implement driver and guarded HTTP transport; test loopback only. Tokenize actual complete scripted inputs and produce readiness estimates.
- [x] Close prior live-readiness debt with meaningful tests: journal concurrent claim/event cap/bad creation, every reviewer own memory/partner in fourcells, late barrier rollback and distinct-round cumulative score, malformed top-level request error.
- [x] Verify read-only interrupted-state report; full V8/root/V7 tests/raw hashes; fresh review and one RED->GREEN material fix pass.
- [x] Freeze bounded technical manifest/proposal and push; ask user to approve8technical deliveries/15USD only when concrete and reviewable. No model requests before that answer.

Implementation and review complete. Technical manifest publication is the last preparation step; paid launch awaits explicit approval.
