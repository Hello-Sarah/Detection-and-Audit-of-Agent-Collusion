# V8.1 release checks

25 October 2026 HKT. No new model/API calls or spending. The user authorized interface repair, offline review, prospective freeze and estimate, not live execution.

## Validation

- Six behavioral interface regressions: RED against copied original, GREEN after patch. Real adapter/journal/source data; tool-returned method submitted and scoredQ2, enum rejection before lock, actionable schema errors and no untrusted value echo.
- Revised full suite105/105 passed with local HTTP fixtures permitted. Original V8 regression97/97 and root23/23 passed.
- Fresh reviewer: no Critical/Important/Minor findings;34focused tests passed. Its full suite passed103with two sandbox-denied loopback binds; those tests pass in the parent105/105 permitted run. Reviewer did not edit files or call models. This independent reviewer is not Claude Code; external Claude review is still available via CLAUDE_REVIEW_REQUEST.md.
- Scripted readiness:64fixture requests,8safe Q2 deliveries, complete serialized inputs1,273–6,224tokens;204,296serialized tokens total. Not provider counts, actual costs or model behavior.
- Original V8 source has no tracked diff. Original pilot and followup hash manifests verify. Old raw labels/human fields/scores remain unchanged.

## Freeze and approval boundary

TECHNICAL_MANIFEST.json is generated after the source commit and binds all Python/runtime requirement files, inherited amended designs, revision plan, prospective formal allocation and exact dataset hash; offline readiness and tokenizer are also pinned. A new manifest does not authorize spending. Run the technical check command to verify it.

The frozen formal allocation is a prospective schedule, not a formal executable runner. A reviewed formal execution path is still required after the revised technical gate. Revised8delivery gate and formal64delivery allocation each require a separate approval/cap; old permission cannot be reused. No automatic formal start or new run directory was created.

## Costs

Standard uncached rates were verified on25October2026 from https://developers.openai.com/api/docs/pricing : inputUS$0.25/outputUS$2.00per million. ReserveUS$0.108192per request at400,000input/4,096output tokens. Revised technical128requests:US$13.848576ceiling, proposed cap15. Formal1024requests:US$110.788608ceiling, proposed cap115. Combined ceilingUS$124.637184; proposed separate caps total130. These are worst-case token holds, not expected spending. Old pilot extrapolationUS$1.261852for64deliveries is only a rough planning illustration, not a forecast. Reverify rates before any live launch.
