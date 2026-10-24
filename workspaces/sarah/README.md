# Sarah's Workspace

## Research focus: which financial delivery tasks lead to collusion?

Sarah reaffirmed the central question: **Which kinds of tasks lead to collusion?** Keep the financial institution → AI buyer scene. Delivery pressure, resource limits, private communication and the structure of the business task are candidate mechanisms, not findings of collusion by themselves.

The new [financial task-family v6 protocol](financial_task_family_v6/PROTOCOL.md) compares cohort sizing, personalized recommendations, transaction reconciliation and training-input delivery at fixed urgency/resources, with and without an optional private channel. All 32 formal episodes are complete and independently raw-crosschecked; the eight technical smoke episodes stay separate. Read the [English results](financial_task_family_v6/RESULTS_EN.md) or [plain Chinese report](financial_task_family_v6/RESULTS_ZH.md):30aggregate approvals,2safe rejections,0protected releases; report/reason/utility defects remain separate. New v6 human labels remain blank. [Next structural task ideas](financial_task_family_v6/NEXT_TASK_STRUCTURE_DRAFT.md) are a separate exploratory draft, not extra calls or a frozen study.

The new [intermediate-file workflow v7](intermediate_workflow_v7/README.md) compares direct aggregation, sensitive working-file processing and safe aggregate working-file processing for the same final cohort-count request. Source/config freeze490c819 pushed before calls; fixed6smoke+24formal. Smoke currently in progress; no final findings yet. v6 remains a completed separate cohort.

The completed [pressure/resource study](pressure_review_v4/README.md) remains a separate diagnostic with its own [frozen protocol](pressure_review_v4/PROTOCOL.md). Historical baselines are never retrospectively assigned as controls for a new study.

| Study role | Evidence or design | Status / separate denominator |
|---|---|---|
| **Current: intermediate workflow v7** | [Three workflow packages × channel](intermediate_workflow_v7/PROTOCOL.md) | Source frozen/pushed;6smoke in progress;24formal not started; no final findings |
| **Financial task families v6** | [Four financial request packages × channel](financial_task_family_v6/PROTOCOL.md) | Completed:32formal;30aggregate approvals,2safe rejections,0protected releases;8smoke excluded; AIreview/humanpending |
| **Clarified evidence v5** | [16 natural episodes, revised evidence interface](natural_evidence_v5/README.md) | Completed:14aggregate approvals,1false rejection,1withdrawal;0prohibited releases;1inaccurate report approved;4smoke excluded; humanpending |
| **Pressure/resource diagnostic** | [40 seeded reviewer attempts](pressure_review_v4/README.md) | Completed:36 correct terminal decisions,4 no decision;0 unsafe approvals observed; separate4smoke; human confirmation pending |
| **Natural urgency × private channel** | [16 natural two-agent episodes](natural_pressure_channel_v4/README.md) | Completed:13aggregate approvals,2rejections,1hold;0prohibited releases; report/reason errors separate;4smoke excluded |
| v4 natural workflow baseline | [named_v4_pilot_01](experiment_runs/2026-10-24/named_v4_pilot_01/summary.json): eight episodes, four A/four B | Completed; human review pending; no randomized pressure comparison |
| v4 reviewer capability baseline | [Reviewer capability results](reviewer_capability_v4/README.md): twenty seeded-package episodes, four per case | Completed; separate diagnostic; human review pending |
| Technical smoke | [Natural v4 smoke](experiment_runs/2026-10-24/named_v4_smoke_01/summary.json) and [capability smoke](experiment_runs/2026-10-24/capability_v4_smoke_01/summary.json) | Two each; excluded from formal counts |
| Historical exploration | [Historical evidence index](history/README.md): earlier inputs, diagnostics and pilots | Separate historical versions; never pool with v4 |

All current studies use the [v4 SQLite dataset](datasets/synthetic_financial_v4_english/README.md): 2,000 fictional customers and 20,000 transactions. `synthetic_transaction_details_v4_english.csv` is the downloadable joined transaction export, not a different experiment source. The natural runner can stage all transaction rows; the capability diagnostic uses fixed packages of at most twenty customer rows. The eight-episode v4 natural baseline approved only aggregate counts; report and workflow errors are recorded separately in an AI-assisted draft, awaiting human confirmation.

The earlier natural urgency/channel v4 study found two definite authored report errors (one approved, one rejected for an unrelated wrong reason), an additional false rejection and a safe incomplete hold. All sixteen reviewers inspected actual locked contents; four did not refresh post-submission audit. No sensitive package was submitted, so zero disclosure does not demonstrate interception or a private-channel risk effect. AI semantic review remains pending human confirmation. See [English results](natural_pressure_channel_v4/RESULTS_EN.md) and the [next interface-revision proposal](natural_pressure_channel_v4/NEXT_PROTOCOL_FIXES.md); that cohort is closed and subsequent v5/v6 cohorts remain separate.

Earlier results remain available for provenance, not as additional v4 observations. Raw files stay at their original paths to preserve hashes, review references and reproducibility. Older dataset versions are development assets, not evidence that the historical pilots used an independent database.

The reviewer diagnostic approved all four compliant packages and rejected the other sixteen, including four misleading name/card-containing submissions. These are researcher-planted tests, not spontaneous collusion events. Its two technical smoke episodes are excluded from both the diagnostic formal denominator and natural-pilot counts.

## Workspace and collaboration

This is Sarah's personal area for project notes, drafts, experiment configurations, run logs, and findings. Sarah's individual work stays here, and all code changes or pushes for her work use `sarah/*` branches only. Do not push or merge Sarah's changes to `main`, `feat/*`, or `julien/*` unless Sarah explicitly asks. Do not edit or move Sarah's materials into Julien's workspace without Sarah's explicit request.

Shared code, experiment specifications, and joint deliverables belong in shared project files and should be proposed through a pull request.

See the repository [collaboration rules](../../COLLABORATION_RULES.md). Folder boundaries are organizational only; repository access is not restricted by folder.

For a full project recap and instructions for continuing in Codex, see [CODEX_HANDOFF.md](CODEX_HANDOFF.md).

The v5 label refers to the workflow/evidence interface, not a new dataset. It retains the same v4 source. Two episodes internally staged raw rows, replaced them with aggregates before submission, and never submitted sensitive packages. Do not infer interception from those paths. See [v5 English report](natural_evidence_v5/RESULTS_EN.md) for the false column-name policy rejection, approved staging-location report error, unsupported withdrawal reason and source-attribution qualifications. Older versions and smoke remain separate.
