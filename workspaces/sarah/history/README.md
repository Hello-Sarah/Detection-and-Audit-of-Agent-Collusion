# Historical exploration — excluded from the current v4 pilot

These records document earlier development and exploratory work. **They did not use the v4 English-name dataset and must not be counted with the current eight-episode pilot.** No raw evidence has been deleted, relocated, relabeled or rewritten. This is a navigation archive; original paths remain stable.

| Historical material | What it represents |
|---|---|
| [Scripted controls](../experiment_runs/2026-10-24/plumbing_controls.jsonl) | Seven hand-authored logging controls; not live agent evidence |
| `live_smoke_*` in [dated run directory](../experiment_runs/2026-10-24/) | Earlier v1 diagnostics, including preserved failures; not current smoke or pilot |
| [workflow_v2](../experiment_runs/2026-10-24/workflow_v2/) | Two historical v2 smoke episodes on hardcoded small synthetic inputs |
| [pilot_v2_01](../experiment_runs/2026-10-24/pilot_v2_01/) | First eight historical v2 pilot episodes; separate human-confirmation layer |
| [pilot_v2_02](../experiment_runs/2026-10-24/pilot_v2_02/) | Eight additional historical v2 episodes, chosen after the first results |
| [Historical English brief](../pilot_research_results_2026-10-24_en.md) | Reports both historical pilot batches, 16 episodes; not v4 results |
| [Historical Chinese brief](../pilot_research_results_2026-10-24.md) | Reports only the first historical eight-episode batch; not a translation of the later 16-episode English brief |

The older pilots used the root runner's hardcoded synthetic rows, not any later standalone CSV/SQLite dataset. Dataset [v1](../datasets/synthetic_financial_v1/README.md), [v2 large](../datasets/synthetic_financial_v2_large/README.md) and [v3 Chinese names](../datasets/synthetic_financial_v3_named/README.md) are retained development versions. Do not retrospectively attribute their rows to the earlier pilot trajectories.

For the current study, return to the [main workspace index](../README.md) and [natural v4 results](../named_data_experiment/results_2026-10-24_en.md). The v4 technical smoke remains separate from its main pilot. The original [reviewer-capability design](../next_round_reviewer_capability_design.md) remains a historical proposal; its separately authorized [v4 implementation and completed diagnostic](../reviewer_capability_v4/README.md) has its own twenty-episode denominator and is never pooled with natural episodes.
