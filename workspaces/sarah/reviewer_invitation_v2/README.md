# Reviewer invitation diagnostic v2

Independent 16-slot follow-up to reviewer_invitation_01. Sarah authorized the original API and US$3 hard cap; no retries, replacements, automatic resume or formal V8 allocation. See DESIGN.md and PLAN.md.

Changes: explicit decision arguments and current eligible references; enforced consumed manifest, every locked preview and audit before approval. This is a combined interface/procedural change, not a single-factor causal comparison. Wrong approval remains technically possible after inspections, with exact release of protected files; offline fixtures establish this is not a privacy veto.

Verification: parent 18 tests passed (engine, collector, claim, progress); independent reviewer ran 15 engine/collector tests and found no remaining Important/Critical issues after two repairs. Before repair, tests demonstrated missing eligibility hints, approval without audit and incomplete offline fixture checks. These are engineering fixtures, not empirical observations. The older diagnostic and V8.1 raw hashes remain unchanged (171 and 11 checked respectively).

Runtime: existing pinned Python 3.14/tiktoken 0.12.0; key loaded from local ignored .env or environment through existing settings code, never printed/exported. Same official endpoint and gpt-5-mini-2025-08-07 snapshot. Official model documentation rechecked for token rates before freeze; no account invoice validation.

Run only once from the frozen execution bundle using collector.py and the recorded approval. Always retain allocated/unrun, invalid attempts, limits and failures. Summaries separate approval attempts, prohibited approval attempts and actual protected release. Labels remain unreviewed and human fields null.
