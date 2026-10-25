# V8 technical pilot — approval proposal

Status: ready for a bounded technical pilot; no V8 model calls made. Human approval remains required.

- Scope: S1F1 and S0F0, one cohort each, two rounds and four deliveries per cohort: exactly eight planned deliveries. This checks integration, not scientific effects.
- Model: gpt-5-mini-2025-08-07, official OpenAI Chat Completions endpoint, standard tier.
- Limits: at most 128 requests, 4096 completion tokens per request, USD15 total enforced by a persistent reservation ledger. No retries, replacement tasks or automatic formal experiment.
- A full 400000-input-token plus4096-output-token reservation costs USD0.108192 at standard uncached rates; 128 reservations total USD13.848576. This is a conservative ceiling, not expected spending. Recheck [official pricing](https://developers.openai.com/api/docs/pricing) before launch.
- Any timeout, uncertain billing, integrity failure or failed accounting stops the allocation. Unknown cost retains its full hold. Preserve partial/unrun slots; do not silently resume or invent outcomes.
- This technical-only stop rule overrides the general design section8 continuation wording. Formal continuation is not implemented or approved.
- Exact source/data hashes, tokenizer, allocation and order are pinned in TECHNICAL_MANIFEST.json. Launch refuses changed inputs, existing output directories or missing explicit approval/cap.
- Provider usage calibration happens within these eight deliveries, without extra calibration calls. Offline serialized token counts are not exact provider prompt counts or observed model behavior.
- Export SQLite journals, complete JSONL, summary and blank/unreviewed human evidence forms. No automatic semantic collusion labels.

Approval requested: eight technical deliveries, maximum USD15, stop on anomalies. Formal experiments require a separate decision.
