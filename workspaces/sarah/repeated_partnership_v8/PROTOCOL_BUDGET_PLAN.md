# V8 provider protocol and budget reservation — offline phase

User authorized next step after615d26d. Same Sarah checkout/branch; execute inline with TDD and one fresh review. This is not API/allocation/spending approval. No credential read, model client, HTTP implementation, CLI or live call.

## Sources and pricing assumptions (read 2026-10-25)

Official model https://developers.openai.com/api/docs/models/gpt-5-mini preserves gpt-5-mini-2025-08-07,400000context. Official Chat Completions OpenAPI https://api.openai.com/v1/chat/completions confirms single-choice messages/tool calls/finish reasons/usage. Search/fetched schema examples plus official advanced usage https://developers.openai.com/api/docs/guides/advanced-usage establish billed prompt/completion tokens and local-count caveats. Pricing https://developers.openai.com/api/docs/pricing standard gpt-5-mini input$0.25/output$2.00 per million; cached discount ignored conservatively. Reverify at freeze, standard service tier only, text/function tools only. Rates refer to model token charges, not other account activity.

No tiktoken installed. Optional local estimate must explicitly report serialized-body token count, not exact provider prompt count/hard billing bound; no four-characters shortcut or model fallback. Exact tokenizer and actual provider-format calibration still a live gate.

## Modules

protocol.py builds immutable UTF8 request bytes from role input: pinned model,n1,tool_choice auto,max_completion_tokens4096,stream false,store false,service_tier default. Inputs/tools cloned before use; no credentials. parse_response validates exact model,one assistant choice, tool call structure/unique original IDs, finite JSON object arguments, usage integer totals/bounds, output including reasoning. Ordinary malformed tool arguments remain invalid tool arguments with original raw data retained, never repaired into an action. Malformed envelope/missing usage stops. length/refusal carries no executed actions; no retries. Preserve original response/IDs and explicit parsing status for future driver integration; no synthetic model statements.

budget.py is a separate exclusive0600 SQLite ledger with approved-cap-reference metadata, integer nanoUSD amounts, bound rates/model/pricing reference, at most1152preallocated requests. All approval refs in tests are explicitly fixtures; no production budget exists. Each unique request reserves400000input+4096output at standard uncached rates BEFORE injected transport, independent of local token estimates. One outstanding reservation, no duplicate dispatch/retry. Success settles actual valid usage; unknown usage/timeout/malformed response retains full reservation and blocks further dispatch. Persistent reservations survive reopen; no refunds by guess. Transport is an injected test callable receiving immutable bytes and90second timeout, not an HTTP client.

Worst-case per-call token reservation$0.108192; proposed128technical requests$13.848576 and1152total$124.637184 are conservative ceilings, not expected cost, approved allocation or requested approval. Need exact tokenizer/input estimate, budget choice, source freeze, recovery and collector integration before live. Offline gate alone cannot constrain external account activity or out-of-band clients.

## Tests and tasks

- [x] RED protocol tests for immutable full input/tool request, pinned caps/model/tier, ordinary text/tool response parsing and original IDs, malformed/duplicate/null fields, invalidJSON tool arguments, length/refusal no execution, bool/negative/missing/inconsistent/excessive usage, optional tokenizer absence fails explicitly.
- [x] RED budget tests realSQLite reservation before injected transport, insufficient cap blocks callback, duplicate/pending/reopened/uncertain cannot redispatch, exact integer settle/refund-known-difference, concurrent ledger connections, malformed/timeout preserves full hold, callback exceptions redacted constant, request count cap, rollback on accounting failure.
- [x] Implement minimal modules with no provider network client; verify scripted dispatch only and existing task/cohort tests.
- [x] Full V8/root/frozenV7 and24V7hash checks; fresh review, one regression fix pass, docs/ledger/push.

Review focus: no spend path before durable reservation; immutable exact bytes; missing/invalid usage cannot free funds; concurrency/reopen and no automatic retry; output reasoning within cap; raw original evidence separate from normalized action args; model/tier/price pinning. ActualHTTP/keys, raw-response-to-TaskAdapter driver integration, exact provider tokenizer/calibration, timeout-to-task outcome, recovery, collector/freeze and semantic labels remain out of this phase. New protocol parser/ledger must not be described as complete live runner.

## Gate evidence

7protocol+9budget tests /75V8total pass; root23/frozenV7 21pass;24V7raw hashes unchanged. Fresh independent reviewer ran all16new tests and found no Critical/Important issue. Deferred minor: malformed top-level build_request list yields AttributeError instead of the constant ProtocolError, before reservation/transport. Raw structurally invalid finite responses are now saved before parsing; caller mutations cannot replace settled evidence. Real simultaneous connection test passes. Previous journal/coordinator test debt remains unchanged. No production approval/cap file, token calibration or real client was created.
