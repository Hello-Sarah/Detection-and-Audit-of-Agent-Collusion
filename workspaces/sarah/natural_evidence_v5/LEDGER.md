# Execution ledger — plan: workspaces/sarah/natural_evidence_v5/PLAN.md

Preflight: clean dedicated sparse checkout, sarah/pilot-run at89f3fb2. Existing Sarah checkout reused per continuity authorization; no Julien paths checked out or modified. No new worktree needed. User opted out of routine questions; scale4+16 announced before calls.
Task1→Task2: same environment APIs/configuration required; new manifest/audit metadata added,collector validator must account for crosswalk. Task2→Task3: same rawformat withaddedmetadata; offlineauditor must accept explicit operational crosswalk keys. Preserve humanlabels and oldesthashes.
Task1 inprogress: unchanged v4 clone only; no revisedbehavior implemented yet.

Task1: crosswalk/threshold regressions RED2expectedfailures→GREEN14/14; root23/23. Additional nofilter/raw20k/hold/rolehistory contracts inherited and green. Metadata derivation verified against realSQLite aggregate query; rawmanifest receives noaggregateproof. Task2 collectoradapted newdatepaths/seed/allpriorraw andhistoricalevidencehashes; noAPIcallsyet.

Finalreview: fixed malformedprotocol continuation blocker. Rootcause: collector errorstrings omitted actualBoundedClient invalidJSON and choice missingmessage KeyError. Integrationtest REDbothcases continued2slots→GREENstopsafterpreservedfirstslot, missingmessage normalized toMalformedassistant. Added actualapprove/withdrawcrosswalkoffset coverage. Suite16/16 plusroot23/23green. No livecalls yet; no unresolvedreviewblockers.

Task2: freeze8510be3beforeanycalls;4smokecompleted with noAPIerrors. Offlinefrozen/history/crosswalk/recipient/refinput/releasehashauditpassed. Smoke02inaccurateseq10attribution,03invalidmixedrolerefsrecovered,04manifestsourcequalification retained in separateAIdraft; rawunreviewed/humanblank. Formal16started, no desiredoutcomegate.

Task2 complete:4smoke+16formal preserved, noAPIerrors/replacements/expansion. Formal14aggregateapprovals1reject1withdraw, allslotsretained. Task3: all20independentlyrawreviewed; separateAIexport/humanblank. Offlineaudits passed frozenhistoricalhashes, globalcrosswalk, rolehistory, recipients, referenceconsumption, actualreleasehash androundcountdown. Reports explain15returnedversus16retrieved, rawstagingnotrawsubmission,definitefalsepolicyreject/reportstorageerror, ambiguities, nocausalclaim. Finalverification/packagingpassed; commit/push executed after this record.

Finalreview: corrected reportwording fixedturnbudget→maximum8/role,16/episode, earlyterminationallowed; actualformal137requests. Source/experimentunchanged. No unresolvedsource/datareviewblockers. Finalfreshsuite16/16+root23/23green; no new livecalls fromtests.

Task3 complete: raw-first independentsemanticreview and finalwordingcorrection integrated; allfrozen/priorhashes+humanlabels+uniqueIDs+credentialscanverified, reports/outputsZIPcheckedCRC/SHA256. Integration: preserve existingSarahbranch/checkout and push onlysarah/pilot-run underuserstandingauthorization, no PR/merge/Julienchanges. No unresolvedrulings orsourceblockers. No extraAPIcalls after20.
