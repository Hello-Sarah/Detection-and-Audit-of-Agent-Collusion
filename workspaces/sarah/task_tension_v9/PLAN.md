# V9 implementation plan

Goal: execute the user-selected36-slot exploratory task-tension diagnostic under a US$10 hard cap.
Architecture: separate versioned engine, allocation/serialization gate and one-shot collector. Reuse frozen V8.1 transports/journal/budget; adapt V2 explicit evidence interface. No historical changes.
Tech: pinned Python3.14/tiktoken0.12.0, unittest, existing direct official API transport.
Spec: DESIGN.md, derived from selected chat design.

- Test-first: allocation4/cell+4controls, factor exposure and same prohibited report/package,6request cap, task-specific full fulfillment and shared score, no unauthorized scripted model history.
- Implement versioned engine and separate mechanical KPI exporter; preserve raw legacy scores and label boundaries.
- Adapt collector to36/216/US$10, source closure and initial hash gates; offline fixtures must demonstrate both safe and unsafe execution capability and failure stops.
- Run suite, independent review, fix Important issues, freeze exact requests/allocation and push before calls.
- Single live execution only; preserve failures/nondecisions and push raw artifacts, separate results/evidence table and next-day handoff. No outcome-driven extensions or inferred intent labels.
