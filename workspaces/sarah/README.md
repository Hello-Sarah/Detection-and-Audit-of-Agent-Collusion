# Sarah's Workspace

## Current research: v4 English-name dataset

Start with the [current results](named_data_experiment/results_2026-10-24_en.md) and [workflow description](named_data_experiment/README.md).

| Category | Evidence | Included in current pilot counts? |
|---|---|---|
| **Current main pilot** | [named_v4_pilot_01](experiment_runs/2026-10-24/named_v4_pilot_01/summary.json): eight episodes, four A/four B | Yes; human review pending |
| Technical smoke | [named_v4_smoke_01](experiment_runs/2026-10-24/named_v4_smoke_01/summary.json): two episodes, one A/one B | No |
| Historical exploration | [Historical evidence index](history/README.md): earlier inputs, diagnostics and pilots | No; never pool with v4 |

The current runner reads the [v4 SQLite dataset](datasets/synthetic_financial_v4_english/README.md): 2,000 fictional customers and 20,000 transactions. `synthetic_transaction_details_v4_english.csv` is the downloadable joined transaction export of that dataset, not a different experiment source. The main pilot is therefore called **based on the v4 dataset**. Eight episodes approved only aggregate counts; report and workflow errors are recorded separately in an AI-assisted draft, awaiting human confirmation.

Earlier results remain available for provenance, not as additional v4 observations. Raw files stay at their original paths to preserve hashes, review references and reproducibility. Older dataset versions are development assets, not evidence that the historical pilots used an independent database.

## Workspace and collaboration

This is Sarah's personal area for project notes, drafts, experiment configurations, run logs, and findings. Sarah's individual work stays here, and all code changes or pushes for her work use `sarah/*` branches only. Do not push or merge Sarah's changes to `main`, `feat/*`, or `julien/*` unless Sarah explicitly asks. Do not edit or move Sarah's materials into Julien's workspace without Sarah's explicit request.

Shared code, experiment specifications, and joint deliverables belong in shared project files and should be proposed through a pull request.

See the repository [collaboration rules](../../COLLABORATION_RULES.md). Folder boundaries are organizational only; repository access is not restricted by folder.

For a full project recap and instructions for continuing in Codex, see [CODEX_HANDOFF.md](CODEX_HANDOFF.md).
