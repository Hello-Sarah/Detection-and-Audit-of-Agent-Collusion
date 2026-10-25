# Subscription-mediated tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Inline execution requested by Sarah; one fresh final review.

**Goal:** Execute one bounded, subscription-authenticated tool smoke with protected research paths denied to role subprocesses.
**Architecture:** A pure envelope/provenance bridge reuses frozen TaskAdapter; a ChatGPT-only CLI launcher captures real outputs under Seatbelt; a one-episode collector exports raw evidence.
**Tech Stack:** Python stdlib, existing SQLite journal, installed Codex CLI, macOS sandbox-exec.
**Spec:** DESIGN.md, approved narrow next-step scope in conversation.

## Global Constraints

Sarah branch/files only; no paid API/Modal,16turns maximum,180seconds/turn, no automatic retry, labels null/unreviewed. Exact-model request gpt-6-sol, no fallback. Unmodified frozen source.

## Review Focus

- Wrong actor or unseen references cannot influence a decision.
- Unconfirmed/malformed CLI output cannot execute tools or receive a score.
- Prepared peer private text never appears in the wrong actor packet.
- OS research-path restrictions cover symlink aliases and writes.
- Native tool events and source changes stop the collector without resume.

## Task1: Envelope bridge and isolation

Files: bridge.py, isolation.py, test_bridge.py, test_isolation.py.
Interfaces: parse_completion(events)->(content,calls,usage); confirm_and_apply(task,actor,packet_hash,call_id,events); profile(protected_paths)->str; probe(profile)->observations.
- [x] Write tests: actual raw workingfile/aggregate/remove/lock/inspect/audit/release flow, wrong actor, private packet separation, malformed/duplicate/native events rejected, no confirmation/score on failure, packet digests, real OS deny aliases/write/read with public control.
- [x] Run unittest; expect missing modules RED.
- [x] Implement minimal validated bridge and profile. Run unittest GREEN.
- [x] Commit.

## Task2: Subscription collector

Files: collector.py, README.md; isolated run folder under Sarah experiment_runs.
Interfaces: launcher(packet,callpath)->actual CLI events; run(output)->one final/partial export.
- [x] Add tests: key-free environment/forced ChatGPT, exact model/flags, exclusive run creation,16turn cap, source integrity; run RED.
- [x] Implement launcher and one-episode collector. Validate offline before any subscription calls.
- [x] Fresh independent review; freeze d3f243e pushed before the smoke. Actual startup/partial-export issues fixed with RED/GREEN after the single stopped attempt.
- [x] Run one subscription episode; retain stopped compatibility failure with no tools/release. Original hashes verified, additive posthoc audit and README updated. No automatic retry.
