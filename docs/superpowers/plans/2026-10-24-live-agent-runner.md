# Live Agent Runner Implementation Plan

> **For agentic workers:** Execute this plan task by task and check each box only after its verification passes.

**Goal:** Add an OpenAI-compatible live model runner for the synthetic two-agent A/B release task, with auditable tool trajectories and an explicit simulated approval gate.

**Architecture:** Keep the existing scripted harness as a plumbing control. Add `live_runner.py` for the API adapter, rotating agent turns, scenario state and tool execution; route completed episodes through the existing `Episode` JSONL format. Dependencies remain Python standard library only. Real model runs must be marked `model_generated`, retain unreviewed labels until human adjudication, and never log API credentials.

**Tech Stack:** Python 3.12+, `urllib`, `unittest`, OpenAI-compatible Chat Completions API.

**Spec:** `experiment_spec.md`

## Global Constraints

- Use only fictional synthetic records and a local simulated release area.
- Condition A has no private messaging tool; condition B has a logged shared message channel.
- Only reviewer approval releases staged artifacts.
- Keep all evidence in the episode trace; do not label live model behavior automatically as collusion.
- Read the API key from `OPENAI_API_KEY`; never serialize it to logs.

## Review Focus

- Missing API configuration fails before any request is sent.
- Malformed model tool calls become logged tool errors, not silent approvals.
- Unauthorized staged rows do not count as delivered until reviewer approval.
- Private messages are absent from A and visible to both roles in B.
- Timeout/API errors leave an incomplete episode and never manufacture a release.

---

## Task 1: Specify live episode behavior

- [x] Add tests using a deterministic fake chat client for A/B tool availability, turn alternation, messaging, submission, approval-gated release, and unreviewed live labels.
- [x] Run the focused test file and confirm it fails because the live runner does not exist.

## Task 2: Implement the live runner

- [x] Add the OpenAI-compatible HTTP client using only the standard library.
- [x] Add role prompts, synthetic tools, shared state, message channel, approval gate and bounded round-robin turns.
- [x] Persist model-generated episodes to JSONL without secrets; leave labels unreviewed.
- [x] Run the focused tests, then the full test suite.

## Task 3: Add CLI and setup documentation

- [x] Add live/scripted mode and run-count, model and turn-limit options.
- [x] Document environment variables and explicitly distinguish model runs from scripted controls.
- [x] Run local smoke checks without an API key and verify the expected configuration error.

## Task 4: Commit and publish

- [ ] Commit locally on `feat/live-agent-runner`.
- [ ] Add the same deliverables to a new GitHub branch based on `research/data-release-collusion`.
- [ ] Verify the branch diff and that no `.env`, credentials, or `.codex/` files were uploaded.
