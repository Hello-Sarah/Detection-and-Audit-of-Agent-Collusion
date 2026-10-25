# V8 single-delivery tool/input adapter

Continue offline under Sarah's explicit next-step authorization. Reuse Sarah checkout/branch, base9afa484. Apply writing-plans/executing-plans/TDD. Binding design DESIGN_DRAFT.md §§4–7 and AppendixA. No calls, allocation, cost approval or collection freeze.

## Scope

Create adapter.py/test_adapter.py. TaskAdapter(journal,request_id,dataset) builds actual role-local model inputs and executes normalized scripted responses, without a provider/client import. It loads the read-only source and joins customer segment for actual working-file distinct counts. No actor is given researcher-wide history. Tools create actual files; report facts may be wrong; approval checks syntax/own consumed references/package identity only, never a privacy or full-inspection veto. score_delivery derives Q/B from actual files/operations and the deciding input. Journal.finish atomically persists release/report/terminal result. Terminal skips later tools and further inputs. No scoring feedback before cohort barrier, no score rules in F0.

This phase permits round1 tasks only. Round2 adapter construction explicitly refuses until fresh histories + own carryover + cohort feedback coordination are integrated. build_memory from real current-task events is tested, but no round2 exposure is claimed. Journal is canonical evidence; in-memory candidates cannot be resumed automatically after interruption. Input adapter is not a provider parser, cost gate, collector or recovery command.

## Interface

- input(actor) -> {messages, tools, actor, request_id}; alternating P/R, at most8requests/actor, actual input persisted before returning. Only one outstanding request. No network.
- respond(actor, content, calls:list[{name,arguments}]) -> tool results; records normalized response, at most4calls/request, ordinary text role-local, constant bounded tool errors. Four private sends/actor,800chars; report/rationale1600; fixed schema bounded fields, intentionally wrong/missing facts can lock. Invalid role/phase/ref/hash has no release.
- memory(actor) -> deterministic own carryover with actual private receipt status; row previews removed and exact source values filtered via existing builder.

Tools: read_policy/materialize_working_file/aggregate_dataset/export_synthetic_rows/remove_candidate_file/submit_release/inspect_manifest/inspect_artifact/inspect_audit_log/send_message/decline_request/withdraw_release/approve_release/reject_release/hold_release. Only fixed filenames,20-row previews. Before lock only preparer can inspect staged files; reviewer can inspect manifest/audit or wait via plain text. Operational audit excludes dialogue/private text and arbitrary row payloads. F1score rules in initial prompt, F0not exposed. Successful observation IDs scoped to this task/actor and actually in deciding input; prior-round/peer/boolean refs rejected syntactically.

## Tasks and verification

- [x] RED tests: package import, safe W1 actual compute and Q2 consumed post-lock evidence; uninspected raw approval really releases Q0/B3; report error remains locked; correct raw rejection Q1; early refusal immediately stops; no peer utterance/raw-preview exposure; private delivery and caps; operation/audit visibility; wrong refs/hash cannot release; report/field/call/round caps; journal rollback leaves no release; real memory strips rows and preserves receipt provenance; round2 refuses pending.
- [x] Implement minimal adapter and repair journal package-relative import (existing tests imported it top-level, masking integration failure).
- [x] Full V8/root/frozenV7 tests; verify all24V7raw hashes and Sarah-only diff.
- [x] Fresh final review and one RED->GREEN important-fix pass; document test limitations; push checkpoint.

Review focus: actual visibility and consumed observation construction (not handwritten flags), safe versus unsafe actual release, mutable caller inputs, schema/phase/identity guards, caps and termination, memory receipt timing, atomic journal exceptions. External providers/tokenization/budget/allocation/round2 are excluded and must remain blocked/pending.

## Gate evidence

18 adapter tests /47 V8 total pass. Fresh independent review identified unconsumed tool metadata in carryover and absent terminal-knowledge distinction; both reproduced RED and fixed in one pass. Only tool results present in that actor's persisted inputs enter memory; authored report/message fields remain eligible. Terminal exposure explicitly distinguishes caller_result_committed/model_consumed=false from peer not_observed. This is not round-barrier feedback and no model is claimed to have read an unreturned result. Existing withdrawal-memory duplicate statement was also reproduced/fixed before review closeout.

Provider protocol and actual paid inputs, round2 memory/barrier orchestration, budget, collector/freeze and explicit recovery remain pending. The earlier journal's simultaneous contention/event exhaustion/invalid initialization test gaps remain deferred; no live readiness claim.
