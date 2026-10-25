# V8.1 stopped-request investigation

The live batch remains stopped. The final TRANSPORT_ERROR has no preserved provider response or exception family. Its specific network/protocol root cause is **unknown**. No old request was retried, no hold was released and no past score/label changed.

## What was reproduced offline

Two local HTTP fixtures each generated one request and left frozen V8.1 last_failure=null: an abrupt disconnect raised RemoteDisconnected; an oversized response raised TransportFailure. REPRODUCED_GAPS.json records these scripted faults. They reproduce the logging gap, not the live event. Run reproduce_gaps.py from the repository root with the pinned v8-runtime Python; no model endpoint is used.

## Candidate diagnostic fix

candidate.py subclasses the frozen transport, preserves endpoint/timeouts/redirect/no-retry behavior, rethrows original exceptions, and adds allowlisted failure families plus elapsed time. It clears diagnostic state at call entry. It never logs raw exception messages, payloads, URLs, partial response bodies or credentials. It does not settle billing or resume runs.

This candidate is not integrated into the V8.1 launcher. A later separately frozen integration must persist last_diagnostic together with run provenance. The in-memory property alone does not add diagnostics to old evidence or guarantee persistence after a crash.

Some TLS failures wrapped by URLError are normalized by the old parent to CONNECTION_FAILURE before the wrapper sees them; they remain generic connection diagnostics. This limitation is intentional and tested. Do not infer a specific TLS/network cause from that code.

## Verification and review

Five initial regressions failed against the frozen transport (four assertions and one missing diagnostic attribute) and passed after adding the wrapper. A fresh reviewer found an in-flight stale-state issue; a new failing regression reproduced it, and the one-line entry reset made it pass. Final11candidate tests and23root tests pass, using local fixtures only. Additional tests cover exception identity, timeout, incomplete read, broken pipe, direct/wrapped TLS, interruption, HTTP redirect/error, invalid JSON, success/failure reset, unknown-error value redaction, and unchanged uncertain-hold/second-dispatch blocking.

Independent code/design review was performed. The reviewer could run two injected tests; six then-existing socket-dependent tests were sandbox-blocked, not proven failures. The parent ran the full permitted suite. No Critical findings; Important diagnostic reset was fixed with RED→GREEN. The proposed invitation study was expanded to specify input authority/order, evidence/annotation rules, allocation and missingness denominators. Minor Chinese stimulus-summary ambiguity and diagnostic coverage/TLS limitation were addressed. No deferred code findings remain; external live root cause and future integration remain limitations, not solved incidents.

Next: review and approve a separately versioned integration and new bounded collection. The stopped run and unknown cost retain their original evidence and reservation. No new model calls are authorized by this candidate.
