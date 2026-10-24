# Sarah's Workspace

## Research focus: review quality under delivery pressure and scarce resources

The central question is now: **When delivery is urgent or review resources are scarce, do agents still verify evidence and uphold release standards?** See the [new pressure/resource design](pressure_resource_review_design_v1.md). It is a prospective draft, not an executed pressure study. Existing results are retained as preliminary workflow and capability baselines, not retrospectively assigned control groups.

| Study role | Evidence or design | Status / separate denominator |
|---|---|---|
| **Next main study** | [Delivery pressure × review resources](pressure_resource_review_design_v1.md) | Design only; no new runs; proposed scope needs execution authorization |
| v4 natural workflow baseline | [named_v4_pilot_01](experiment_runs/2026-10-24/named_v4_pilot_01/summary.json): eight episodes, four A/four B | Completed; human review pending; no randomized pressure comparison |
| v4 reviewer capability baseline | [Reviewer capability results](reviewer_capability_v4/README.md): twenty seeded-package episodes, four per case | Completed; separate diagnostic; human review pending |
| Technical smoke | [Natural v4 smoke](experiment_runs/2026-10-24/named_v4_smoke_01/summary.json) and [capability smoke](experiment_runs/2026-10-24/capability_v4_smoke_01/summary.json) | Two each; excluded from formal counts |
| Historical exploration | [Historical evidence index](history/README.md): earlier inputs, diagnostics and pilots | Separate historical versions; never pool with v4 |

Both completed v4 studies use the [v4 SQLite dataset](datasets/synthetic_financial_v4_english/README.md): 2,000 fictional customers and 20,000 transactions. `synthetic_transaction_details_v4_english.csv` is the downloadable joined transaction export, not a different experiment source. The natural runner can stage all transaction rows; the capability diagnostic uses fixed packages of at most twenty customer rows. Eight natural episodes approved only aggregate counts; report and workflow errors are recorded separately in an AI-assisted draft, awaiting human confirmation.

Earlier results remain available for provenance, not as additional v4 observations. Raw files stay at their original paths to preserve hashes, review references and reproducibility. Older dataset versions are development assets, not evidence that the historical pilots used an independent database.

The reviewer diagnostic approved all four compliant packages and rejected the other sixteen, including four misleading name/card-containing submissions. These are researcher-planted tests, not spontaneous collusion events. Its two technical smoke episodes are excluded from both the diagnostic formal denominator and natural-pilot counts.

## Workspace and collaboration

This is Sarah's personal area for project notes, drafts, experiment configurations, run logs, and findings. Sarah's individual work stays here, and all code changes or pushes for her work use `sarah/*` branches only. Do not push or merge Sarah's changes to `main`, `feat/*`, or `julien/*` unless Sarah explicitly asks. Do not edit or move Sarah's materials into Julien's workspace without Sarah's explicit request.

Shared code, experiment specifications, and joint deliverables belong in shared project files and should be proposed through a pull request.

See the repository [collaboration rules](../../COLLABORATION_RULES.md). Folder boundaries are organizational only; repository access is not restricted by folder.

For a full project recap and instructions for continuing in Codex, see [CODEX_HANDOFF.md](CODEX_HANDOFF.md).
