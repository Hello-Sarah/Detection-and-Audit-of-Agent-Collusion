# Natural evidence v5 Implementation Plan

> For agentic workers: use superpowers:executing-plans, inline execution. Tests before behavior changes; one independent whole-source review before freeze.

**Goal:** Execute the approved next natural study after clarifying evidence interfaces.
**Architecture:** New Sarah-local runner/collector copied from frozenv4, with only the four protocol revisions. Original source/evidence untouched; standard-library offline integrity/review exports.
**Tech Stack:** Python3 standard library, configured OpenAI-compatible client, SQLite read-only.
**Spec:** PROTOCOL.md; predecessor natural_pressure_channel_v4/NEXT_PROTOCOL_FIXES.md.

## Global constraints

Sarahpaths/sarahbranch only. Same dataset/model/8turns/4096tokens/90s;20attempts maximum(4smoke16formal), four/cell. No deterministic privacy filter, hiddenanswerleak or altered humanlabels. Separate versions/denominators. Freeze beforecalls. Preserve interruptions/failures, no desired-outcome retries.

## Review focus

Crosswalk references must resolve actual sameoperation events even with private/dialogue gaps; no message text leaks. Aggregate derivation must not attach to raw manifest. Policythreshold10 differs actualminimum1000; observation not transformed into release oracle. Terminalhold cannot allow correction/release. Incorrect approval must still deliver raw20krows; invalid/unobserved decision refs rejected independently of reportprovenance.

### Task1: Interfaces and regression tests

Files: runner.py,test_natural.py,test_evidence.py. Consume frozenv4 environment; produce same _Environment/run_live_episode APIs with auditcrosswalk and explicitaggregateproof.
- [ ] Write regression tests against unchanged clone: correct metadata minimum/proof, crosswalk amidst message gaps, rawproofabsence, false report not silently edited/filtered, terminalhold state.
- [ ] Observe expected failures, implement minimal changes, pass new tests and inherited9contracts plus root23suite.
- [ ] Independent whole-source review before sourcefreeze; fix substantive defects with red→green verification.

### Task2: Prospective collection

Files: collect.py, PROTOCOL.md, frozen manifests under2026-10-25/natural_evidence_v5_{smoke_01,01}.
- [ ] Adapt collector only newpaths/seed/sourcehashes, include every prior completed rawfile hash and all older evidence-file hashes; neutral outcome-independent smoke gate.
- [ ] Freeze/commit source+configuration+schedule; verify APIkeypresence without printing, owner-only env; run4smoke then16formal.
- [ ] Preserve checkpoint/allocatedslots; stop only systemicfailures, never replacebehavioraloutcomes.

### Task3: Evidence/report

Files: audit_evidence.py, new JSON factualsummary, blankhumanworksheet, separateAIreviewdraft, English/Chinese results, Sarahindex/handoff and outputsZIP.
- [ ] Audit actualrequesthistory, crosswalk, message recipients, frozen/oldhashes, actualreleasehashes, tools/errors/tokens/turncaps, rawunreviewed/humanblank.
- [ ] Read each raw episode first for factualclaims/reasons; compare factualsummary afterwards. Independent AI cross-check, no groundtruthclaim.
- [ ] Report allallocations and qualifications; separate version/smoke. Credentialscan/diffcheck; commit/push onlysarah/pilot-run; user-facing deliverables onlyouteroutputs.
