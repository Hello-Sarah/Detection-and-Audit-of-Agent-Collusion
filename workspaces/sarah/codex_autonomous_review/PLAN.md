# Autonomous review implementation plan

> REQUIRED SUB-SKILL: superpowers:executing-plans; implement inline with test-driven-development and one fresh review.

Goal: one subscription-only autonomous exploratory smoke, not a prescribed safety route or formal comparison.
Spec: DESIGN_DRAFT.md; Sarah explicitly requested implementation/testing after agreeing to direction.
Architecture: new TaskAdapter subclass replaces both inherited solution layers; new collector reuses tested CLI auth/provenance/isolation helpers, without modifying frozen source.
Constraints: one episode, max16fresh CLI turns/8per actor,4mediated calls/turn,180seconds/CLI, gpt-6-sol requested, no retry/resume, no Platform/Modal, null human labels. Refusal/early termination is retained, no replacement. Three unused structural journal slots are inactive.
Review focus: no residual guidance in complete actor packet; enum/tool result/validator alignment; rejected invalid report cannot lock; wrong actor/private visibility; no hidden disclosure veto; original source frozen and new hashes before collection. Missing named inspections is coverage, not automatically a policy violation. Inherited Q/Bscore is diagnostic only and not a research label.

Task1: model.py plus test_model.py. RED missing module. Replace role histories, expose method enum and returned identifier, validate report structure without truth repair, preserve tool/release semantics. GREEN full-packet and actual tool-state tests.
Task2: collector.py plus test_collector.py. RED missing module. Fresh ChatGPT-only launcher with neutral formatting wrapper, no GUIDE. Exclusive one-slot manifest/output, source guards, raw partial export, no outcome chasing. GREEN pure collector validation plus real OS probe inherited. Fresh final review, fix material findings with RED/GREEN.
Task3: commit/freeze/push before one live subscription episode. Audit raw role packets, tool/release content and frozen hashes; preserve outcome, no reruns. Update findings and push. No additional allocations.
