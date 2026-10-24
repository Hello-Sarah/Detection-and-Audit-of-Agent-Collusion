# Implementation plan: data-release collusion pilot

## Scope and stop condition

Deliver a local, reproducible harness for synthetic release tasks, an explicit
episode rubric, and a English-language demo that distinguishes constructed examples
from model observations. No real financial data, external release destination,
or claim of model behavior is in scope until API-backed runs are collected.

## Work breakdown

1. **Freeze design** — define the prohibited row-level release, A/B channel
   manipulation, evidence criteria, and episode labels. Output:
   `experiment_spec.md`.
2. **Build harness** — synthetic fixture; aggregate and row-level simulated
   export; approval gate; append-only JSONL trace; private messages only in B.
   Output: runnable local experiment and schema.
3. **Validate plumbing** — unit tests for condition isolation, event sequence,
   approval/release semantics, and classification. Scripted traces are controls,
   not model-generated samples.
4. **Run real agents** — configure an OpenAI-compatible model endpoint and key,
   freeze model/version/prompts, then run matched A/B trials. Target 4 per
   condition as a pilot; report failures and exact denominators.
5. **Review and communicate** — label each episode against the three required
   evidence elements; update demo with clearly marked observed data; report
   limitations and avoid generalizing from a small pilot.

## Progress

- [x] Design and classification criteria are specified in README.
- [x] Local synthetic harness and JSONL trajectory output implemented.
- [x] Plumbing tests pass.
- [x] OpenAI-compatible live two-agent runner, logged B-channel messages, alternating turns, and simulated approval gate implemented.
- [ ] Real model A/B runs (no provider key configured in this environment).
- [ ] Blind episode review and conclusions.
- [ ] Replace any hand-authored demo traces with links to clearly labeled run data.

## Reuse decision

The Poseidon Research starter / Colosseum is useful as a reference for its
condition structure, multi-agent trajectories, and experiment orchestration.
Its existing tasks are Jira/hospital workflows, so the financial data-release
tools still need a custom environment. This first MVP uses a small independent
harness to keep setup light and avoid copying upstream source without a clearly
identified license. Revisit direct integration if the project expands beyond a
small pilot and license/installation costs are resolved.

## Rollback points

- `main` is the untouched snapshot of the original README and demo.
- Work is isolated on `research/data-release-collusion`.
- To return to the original state: `git switch main`.
- To discard the feature branch after switching away: `git branch -D research/data-release-collusion`.

The live runner is isolated on `feat/live-agent-runner`; return to the previous
MVP with `git switch research/data-release-collusion` or to the original demo
with `git switch main`.
