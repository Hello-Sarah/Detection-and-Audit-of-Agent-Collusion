# Transport diagnostics investigation and candidate patch

Scope: offline investigation and a separately versioned, unintegrated transport candidate. Do not modify frozen V8.1 or raw evidence, release its uncertain hold, replay failed requests, or call a model API.

Observed failure: final reservation TRANSPORT_ERROR, raw_response absent, transport.last_failure null. Specific exception/root cause cannot be reconstructed.

Reproduction: old transport leaves last_failure null for both a local abrupt disconnect (RemoteDisconnected) and oversized response (TransportFailure). This proves a diagnostic gap, not which fault occurred in the live run.

Implementation: subclass frozen HTTPTransport, preserving endpoint, timeout, no redirects/retries and original response handling. Record only allowlisted exception-family/failure constants and elapsed time. Catch and re-raise original exceptions; no retry, accounting settlement or semantic outcome modification. Candidate is not integrated into any live launcher.

Tests first: local disconnect and oversized-response diagnostics; successful exchange then failure reset; controlled unknown exception must not echo values; budget integration retains uncertain reservation and blocks second dispatch. Local tests never call OpenAI.

Next: independent candidate review, then explicitly decide a new version/gate and its cap. Old batch remains stopped; formal execution path still unreviewed.

## Offline continuation (supersedes the unintegrated status above)

Sarah authorized offline integration. `PersistentTransport` now fsyncs a call-ID/payload-hash dispatch marker before network dispatch and a bounded result/failure record afterwards. `launch.py` is a separately named technical-only runner with new IDs and original dependency content hashes. It does not modify or resume the frozen V8.1 runner. No execution manifest or new paid-run approval has been issued for this integration.

New tests exercise budget-linked persistence, a complete eight-delivery scripted route, failure export with seven pending/unrun slots, refusal without approval, invalid-response distinction, and logging/fsync failures before and after one dispatch. If the process or disk fails after sending, no wrapper can guarantee a final diagnostic; an unmatched dispatch marker and uncertain reservation remain, requiring manual investigation. It never releases the hold or retries.

`source_commit` is explicitly informational HEAD at manifest creation. The authoritative executable snapshot is `source_and_data_sha256`, which also covers dirty/new working-tree files. Committing a manifest does not require changing its informational parent commit. Source/runtime/readiness checks remain mandatory before dispatch.
