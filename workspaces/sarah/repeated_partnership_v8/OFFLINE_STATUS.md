# V8 offline implementation checkpoint — 25 October 2026

**Offline foundations implemented; not a live runner, source freeze or API authorization.** No provider/API calls were made. These scripted tests are not experimental observations or collusion results.

## Completed

- cohort pairing/partner notice and round barrier; identical cohort-level F1score exposure, F0feedback excludes numeric points;
- own-visible normalized memory whitelist, row stripping, exact-value filtering, bounded fields, fail-closed context checks and immutable input records;
- source-derived actual-content Q/Bscore, real20000-row fulfillment, partial/duplicate counterexamples, required report facts and relevant consumed-review observations;
- fresh independent whole-foundation review:four Important findings fixed with RED→GREEN regressions (submission/reference validity, early-decline actor/state, memory statement whitelist, supported early rejection). No Critical or deferred Minor findings reported;
- final tests:20V8,23root,21frozenV7allpass. All24V7raw hashes unchanged; prior code/evidence/human records untouched.

## What this does not prove / 尚未完成

The modules consume **trusted researcher-normalized records**. They do not yet create/replay actual provider inputs. Actual agent/prompt/tool adapter and live limits, visibility/provenance construction, actual tool integration with atomic release persistence and explicit recovery, exact tokenizer/input-inclusive pricing and enforceable spend ceiling, bounded collector/freeze/audits, and semantic/human labels remain pending. Never treat the scorer as an online oracle or a substitute for human evidence review. Memory filters are field/value filters, not a universal disclosure guarantee.

The proposed2technical+16formal cohorts/72deliveries remain a proposed ceiling, not an executed or approved allocation. No model called, no source freeze, no positive outcome sought. V7case10 remains pending independently.

## Files and offline verification

[Design](DESIGN_DRAFT.md), [中文設計](DESIGN_ZH.md), [implementation plan](IMPLEMENTATION_PLAN.md), [ledger](IMPLEMENTATION_LEDGER.md).

From repository root:

```sh
python3 -m unittest discover -s workspaces/sarah/repeated_partnership_v8 -q
python3 -m unittest discover -s tests -q
python3 -m unittest discover -s workspaces/sarah/intermediate_workflow_v7 -q
```

No APIkey is needed for these offline commands. The frozenV7suite prints mock malformed-provider fixtures; those are not live calls. All new implementation stays inside Sarah's V8directory and on sarah/pilot-run.

## Durable journal checkpoint

The new `journal.py` adds an offline SQLite persistence layer. It reserves four delivery slots before execution, pins the cohort/configuration, prevents automatic reruns of claimed tasks, gates round2, and commits a local release snapshot with its terminal event in one transaction. Interrupted running slots require explicit recovery rather than a guessed outcome. No provider is imported or called. See [persistence plan](PERSISTENCE_PLAN.md).

This is **not yet integrated with actual agent tools**. It accepts trusted future runner/scorer records, not model claims; it does not verify semantic scoring or export to a buyer. Explicit interrupted-run recovery remains unimplemented. The full actor adapter, input/visibility construction, cost gate and collector are still pending. No new experiment has started.

Persistence verification:9 journal tests (29 V8 total),23 root tests and21 frozenV7 tests pass. Fresh independent review found and fixed one transaction/input-mutation defect with RED->GREEN regression. All24V7formal raw hashes unchanged. Deferred coverage before collection: simultaneous writer stress, event-cap exhaustion and invalid initialization matrix. No live readiness claimed.
