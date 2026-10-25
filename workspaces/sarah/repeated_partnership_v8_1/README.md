# V8.1 method contract and validation revision

**Status:** offline revision only; no new model calls. Original V8 source and technical evidence are preserved. Independent code review and frozen-manifest results are recorded in RELEASE_CHECKS.md when available.

## What changes

- aggregate_dataset returns aggregation_method=distinct_customers_from_working_file. The submit schema publishes that enum; the scorer imports the same contract. Descriptions belong in free_text. Nothing repairs a report or inserts correct facts automatically.
- INVALID_ARGUMENTS includes a bounded validation field path and reason: required, type, maxLength, maxItems, range, enum, or additionalProperties. Errors do not echo submitted values or arbitrary property names.
- Scientific conditions, score amounts, role-local text/private delivery, memory rules, early declines, package locking and release behavior are inherited. Incorrect approval can still release protected files. A structured method enum does not make scope claims trustworthy.

## Proposed allocation and cost

FORMAL_ALLOCATION.json fixes four randomized blocks, one cohort per S/F condition per block:16independent cohorts and64dependent deliveries. Pairing is fixed by condition; first/second-round execution orders are balanced within each cell. Seed2026102504. This allocation module has no formal execution command.

| Stage | Deliveries | Maximum requests | Conservative token reservation ceiling | Proposed cap |
|---|---:|---:|---:|---:|
| Revised technical gate, separate | 8 | 128 | US$13.848576 | US$15 |
| Formal allocation, after gate | 64 | 1024 | US$110.788608 | US$115 |
| Both stages | 72 | 1152 | US$124.637184 | US$130 combined separate caps |

These are worst-case reservations of400,000input and4,096output tokens per request at standard uncached GPT-5-mini rates; not expected bills. The completed old pilot cost conservatively US$0.1577315 for8deliveries. A simple eightfold extrapolation is US$1.261852 for64deliveries, but that old two-cell technical sample is not a reliable forecast or a spending guarantee. Inputs, duration and outcomes can differ.

**No spending authorization exists for this revision.** Historical US$15 permission covered the completed old batch only. Reverify current official pricing before launch. First approve a revised8delivery gate; only after reviewing it decide whether to authorize formal collection. No formal launcher is implemented by this revision, so approval alone would still require a reviewed execution path for the64delivery schedule.

## Offline readiness

OFFLINE_READINESS.json measures complete serialized scripted requests, including tools/history/memory, with tiktoken0.12.0 and o200k_base. The64scripted requests are fixtures, not agent observations or actual billed usage. Provider hidden formatting is not locally measurable. These samples cannot establish costs for all possible live trajectories.

Both original and revised batches stay separate. Frozen evidence and human labels must not be modified. A new freeze binds source, data, revision plan and formal allocation; changing any bound file invalidates it.

## Review with Claude Code

Please independently compare this directory with repeated_partnership_v8. Focus on tool/output/scorer method consistency, validation errors without data echo or mutation, retained wrong-approval release capability, preserved experimental conditions, prospective allocation/budget arithmetic and freeze integrity. Read tests and run offline checks only. Do not call any model API, edit original V8 or its evidence, modify labels, or push changes. This request is prepared for Sarah to forward; it does not claim Claude has reviewed V8.1.
