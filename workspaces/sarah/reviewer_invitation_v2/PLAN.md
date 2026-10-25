# Invitation v2 implementation plan

Goal: implement Sarah's selected 16-slot follow-up under a US$3 cap.
Architecture: new versioned engine subclass and separate collector/offline module; reuse immutable V8.1 journal, transport and budget. Do not edit historical modules.
Tech: existing pinned Python runtime and unittest.
Spec: DESIGN.md.

1. Write regression tests for explicit required arguments/eligible evidence, missing approval audit, legitimate safe approval and possible prohibited approval. Observe failures before implementing.
2. Add versioned engine with visible eligibility hints and approval-check enforcement. Preserve journaling and invalid-attempt evidence.
3. Adapt separate offline allocation/collector to new IDs, dependency hashes and exact US$3 approval. Verify offline complete routes and cap/refusal behavior.
4. Check source and historical evidence integrity, freeze exact requests/stimuli and commit/push before calls.
5. Collect once under explicit approval; stop on budget, transport or integrity errors. Preserve raw evidence, blank labels and exact denominators; push collected results separately.
