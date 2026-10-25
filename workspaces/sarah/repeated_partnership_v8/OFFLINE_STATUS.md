# V8 technical readiness — 25 October 2026

Driver, official-endpoint transport, exact-model tokenizer, persistent budget, exports and technical-only launcher are integrated. No V8 paid model call has been made. Approval proposal: eight technical deliveries, maximum USD15, stop on anomalies; no formal auto-start.

97 V8 tests,23 root tests and21 frozen V7 tests pass. All24 V7 raw hashes remain unchanged. Scripted tests and token measurements are engineering checks, not research observations.

Fresh review found one Important issue: a pre-dispatch integrity failure was incorrectly scored as API failure. A failing regression reproduced it; the fix now preserves running state, blank score and full cost hold. Timeout wording is reconciled prospectively in both designs and TECHNICAL_RUN_PLAN.md. Deferred Minor: environment-only configuration still requires a physical.env file; the current configured environment has one. Read-only recovery inventories state but does not resume it.

See [technical proposal](TECHNICAL_RUN_PLAN.md), [offline measurements](OFFLINE_READINESS.json), and [implementation ledger](IMPLEMENTATION_LEDGER.md). Local token counts do not establish exact provider usage; calibration stays within the approved technical allocation. Human labels remain blank/unreviewed.
