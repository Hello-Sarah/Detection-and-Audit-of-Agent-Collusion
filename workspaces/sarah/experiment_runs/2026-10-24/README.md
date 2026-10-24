# Sarah — experiment evidence index

## Current main pilot: v4 dataset

- [named_v4_pilot_01](named_v4_pilot_01/summary.json): eight live episodes, four per condition. This is the current main pilot; human labels remain pending.
- [named_v4_smoke_01](named_v4_smoke_01/summary.json): two separate technical checks, excluded from pilot counts.
- [Current results](../../named_data_experiment/results_2026-10-24_en.md) and [v4 data description](../../datasets/synthetic_financial_v4_english/README.md).

The runner reads the v4 SQLite database; the English-name transaction CSV is a matching export. Do not combine these runs with earlier data/workflow versions.

## Historical exploration

See the [historical evidence index](../../history/README.md) for v1 diagnostics, workflow_v2 smoke, pilot_v2_01 and pilot_v2_02. Raw records remain at their original locations; none of those runs used v4 data.

## Historical scripted plumbing controls

The following seven deterministic scenarios check logging of compliant releases, single-party violations, attempted cover-ups, and coordinated-cover-up fixtures. They are hand-authored controls, not agent behavior, and are excluded from all empirical A/B counts. The earlier statement that live runs were blocked described the environment at control creation; live runs were subsequently collected and are indexed above.

| Condition | Scenario | Harness label |
|---|---|---|
| A | compliant | `compliant` |
| A | single_violation | `single_party_violation` |
| A | coverup | `single_party_violation` |
| B | compliant | `compliant` |
| B | single_violation | `single_party_violation` |
| B | coverup | `coordinated_coverup` |
| B | failed_coverup | `attempt_only` |

Raw logged controls: `plumbing_controls.jsonl`.
