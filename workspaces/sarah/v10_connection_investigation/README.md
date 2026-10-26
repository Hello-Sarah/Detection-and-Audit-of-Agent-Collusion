# V10 connection failure: offline investigation

26 October 2026. **Current sandbox DNS restriction is reproduced; it is the leading explanation of the historical V10 failure, not a retrospectively proven raw exception.** No paid model call, failed-request replay, or continuation of the 23 unrun slots occurred during this investigation.

## What was checked

The original V10 run logged a transport entry followed after 5 ms by `CONNECTION_FAILURE`. There is no provider response, usage data or confirmed model receipt. A local `dispatch_start` marker establishes that the transport wrapper was entered; it does not establish that bytes reached OpenAI.

On the same computer and project Python, address resolution produced this controlled comparison:

| Host | Default restricted execution | Explicit network-enabled execution |
|---|---|---|
| localhost | Resolved | Resolved |
| api.openai.com | `socket.gaierror`, errno 8 | Resolved |
| github.com | `socket.gaierror`, errno 8 | Resolved |
| example.com | `socket.gaierror`, errno 8 | Resolved |

Both DNS-only probes are captured in `default_dns.json` and `enabled_dns.json`. Neither loads credentials or opens an HTTP, TCP or TLS connection. The tool execution context changed; the hostnames, script and Python environment were the same. An earlier pair of manual probes showed the same pattern. The `CODEX_SANDBOX_NETWORK_DISABLED` flag was inherited in both contexts, so that flag alone is not a dependable indicator of actual connectivity; the measured resolution results matter.

The original invocation in this conversation used default restricted execution. The original run did not persist the underlying DNS errno. These findings strongly support an execution-environment restriction as the explanation, while leaving the precise historical exception unproven. They do not establish an OpenAI service outage.

## Runtime and configuration

The read-only audit passed for Python 3.14.3, the pinned tokenizer, `gpt-5-mini-2025-08-07`, the official base URL, and the fixed transport endpoint. A key was configured; its value was neither exported nor sent by these diagnostics. `.env` has mode 600 and is Git-ignored. No proxy configuration was detected by the Python opener; the default CA file and directory exist.

These observations verify local configuration and file access. They do not verify key validity, account balance, model availability, TLS negotiation, TCP port 443 reachability or current API health. Those were not tested.

## Why the old diagnostic cannot identify a unique cause

The frozen `repeated_partnership_v8_1/transport.py` catches non-timeout `urllib.error.URLError`, converts it to `TransportFailure('CONNECTION_FAILURE')`, and sets a generic failure marker. `v8_transport_diagnostics/candidate.py` preserves that marker rather than recording the underlying reason.

In-memory fixture openers reproduced the same persisted diagnostic for both a DNS exception and a wrapped TLS exception. This demonstrates information loss; it does not show that both occurred in V10. Future, separately versioned diagnostics could retain a bounded exception type and errno without saving credential-bearing messages. No frozen transport code was changed here.

## Budget and stop behavior

The original V10 ledger remains stopped with one `uncertain` reservation of 108,192,000 nUSD (US$0.108192), no raw provider response, and no prompt/completion usage fields. The amount is the fixed conservative reservation:

`400,000 reserved input tokens × 250 nUSD + 4,096 output tokens × 2,000 nUSD`.

It is not measured token usage or proof of an actual provider charge. The investigation does not release or settle this hold. An isolated temporary fixture ledger confirmed that one DNS-shaped failure keeps the reservation and blocks a second dispatch; it did not touch the research ledger.

## Integrity and verification

- All 13 original evidence hashes matched before and after the audit.
- The V10 frozen source, data, prior-budget baseline and request bundle still verify.
- The original labels, scores, allocation, raw records and uncertain reservation were unchanged.
- Two local error-normalization fixtures and a temporary-ledger stop fixture passed their assertions.
- Five existing mocked transport regression tests passed: error redaction, timeout handling, per-call diagnostic reset, specific exception handling, and wrapped TLS normalization. No HTTP server or model endpoint was used by these tests.

`local_audit.json` contains sanitized observations. `audit_local.py` is a read-only audit with injected openers; `probe_dns.py` only resolves the four listed names. Diagnostic files are separate from all frozen experiment directories.

## Practical consequence

The earlier launch preflight verified runtime, configuration and hashes but did not test network access in the actual launch context. That omission allowed an otherwise configured run to start from restricted execution. Before any separately authorized future collection, verify connectivity in the exact execution context before making a reservation or sending a credential-bearing model request. DNS resolution would catch the restriction reproduced here, but successful DNS alone is not an end-to-end API readiness check.

V10 remains a stopped engineering run: 1 API-failure slot, 23 unrun, zero confirmed model responses. The current evidence provides no reviewer-behavior or collusion conclusion. This investigation does not authorize a retry, replacement or new batch.
