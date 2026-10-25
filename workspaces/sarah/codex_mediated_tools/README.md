# Codex subscription-mediated tool smoke

A separate engineering test using ChatGPT login. OpenAI Platform API and Modal remain paused. This version executes model-requested tools against the existing synthetic financial database, rather than supplying a completed aggregate in advance.

- One technical delivery, max16 fresh alternating Codex invocations; no retries or formal auto-start.
- Requested model gpt-6-sol; the backend snapshot is not independently exposed.
- Native Codex shell/apps/plugins/browser/memory are disabled. Role receives only its own normalized history; private messages move only via send_message.
- Outer macOS Seatbelt denies direct research-path read/write. Real local probes verify direct read, symlink read and writes fail while a public read succeeds. This is a tested boundary, not universal machine isolation.
- Tools are **host-mediated JSON requests**, not native provider function calls. Existing immutable journal/tool adapter reused unchanged.
- The safe route is requested explicitly to test capability. No natural collusion propensity, repeated-partnership effect or scientific risk estimate follows from this smoke. Never pool with V8, prior GPT runs or Dolos.
- All role packets, original CLI output, normalized tool events and final local releases retained. Human labels remain null/unreviewed.

[Design](DESIGN.md) · [Implementation plan](PLAN.md) · [Ledger](LEDGER.md)

Offline validation: `python3 -m unittest discover -s workspaces/sarah/codex_mediated_tools -q` (macOS Seatbelt probe requires local process permissions, no model).
