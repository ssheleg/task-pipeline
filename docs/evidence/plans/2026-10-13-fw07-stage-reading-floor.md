# FW07 / B-043 — stage reading-floor split

Source-only feasibility packet, frozen against accepted 1.94.0 commit
`4d750573ce53ea4c7ffa2bde192ee35b59acefa7`. Entry:
[RPT task-pipeline/2026-10-13-fw07-stage-reading-floor §Decision proposed](../../reports/2026-10-13-fw07-stage-reading-floor/README.md).
The source owner is task-pipeline; no other member needs a parallel doctrine copy.

## Objective and boundaries

Reduce the stages component loaded at default-profile entry while preserving every
existing obligation, gate and reference meaning. B-043 authorizes a spine plus
stage detail; it does not authorize changing workflow semantics, gate authority,
custom profiles, model selection, user approvals, provider claims or closed/deferred
board decisions. Do not spend the entry's existing headroom on unrelated doctrine.

This packet and report are the only changes in the planning branch. Implementation
requires the parent's bounded review and the current release's completion. Use a
separate implementation branch from accepted release source, merge this packet,
acquire a fresh task lease and remeasure if source bytes changed.

## Requirements frozen for implementation

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FW07-01 | Preserve every source paragraph/obligation | Complete old→new paragraph/section map, with hashes for unchanged text and explicitly reviewed navigation-only edits; no orphan, silent deletion or semantic narrowing |
| FW07-02 | Preserve default stage ids, names, gate types and full gate text | Exact equality to frozen gates, existing pipeline/example/table cross-check, removed/changed-gate negatives |
| FW07-03 | Deterministic on-entry and resume route | One route for each default stage; explicit read-before-work instruction; route id/path equality, missing/unreadable/duplicate/wrong-stage negatives |
| FW07-04 | Preserve custom-profile precedence | A three-stage custom profile does not inherit default stage7 obligations by number; kernel fields remain; source/fixture evidence, no invented host execution proof |
| FW07-05 | Preserve cross-cutting and conditional rules | Run checklist, program loop, Doc Loop, loop guard, audit and user-text rule remain in spine; entry-from-UX, short path, waves, fan-out and resume routes keep their conditions |
| FW07-06 | Keep one normative home per full rule | Gates remain in spine, details in selected files; existing short tables point to the long form; no new duplicated full gate/doctrine surfaces |
| FW07-07 | Update every consumer by meaning | Commit-addressed literal census plus dynamic-reader inventory; source-specific guards/plants follow actual homes; links that resolve but no longer answer fail review |
| FW07-08 | Preserve distributable payloads | Standalone installed skill contains each detail; recursive installer/copy parity, no references to repo-only docs for runtime requirements; Cursor remains self-contained |
| FW07-09 | Keep read-accounting claims honest | Existing unmeasured/unattested behavior remains; no synthetic read completion, no zero for absent hook, no mandatory global preload |
| FW07-10 | Measure entry cost and total tradeoff | Same tokenizer/method before/after; stages entry component strictly decreases with actual routes included; final body/description meet existing budgets; cumulative full-run cost and native billing reported separately, never inferred |
| FW07-11 | Preserve validator effectiveness | Missing detail, dropped internal clause, wrong path, lost gate, wrong profile, stale/duplicate route, broken semantic anchor and no-op plant all fail intended guards; unchanged positives pass |
| FW07-12 | Independent acceptance separates layers | Source equivalence review, focused mutations, owner aggregate, genuine candidate checks and normal merge; native/model comparative result remains NOT_RUN until actual trace-backed execution |

## Work decomposition and ownership

1. **Freeze mapping.** Inventory every paragraph/bullet of stages.md, including content
   after each GATE marker and all non-stage sections. Assign it to the retained spine
   or exactly one stage detail. Mark the pre-existing super-ux prerequisite/fallback
   tension for source-owner interpretation, without silently editing either policy.
   Freeze route filenames and classify every census occurrence. This is reviewable
   before extraction; do not distribute files to parallel writers before it is stable.
2. **Extract and route.** Preserve original stage headings/anchors and gate suffixes in
   stages.md; place details beside existing references. Replace existing entry
   navigation, not unrelated prose, with explicit on-entry/resume loading. Preserve
   the custom profile's own manifest and existing short-path conditions. Keep
   deterministic file selection separate from observed native host loading.
3. **Migrate checks with owners.** One agent owns `test/validate.py` and its plants while
   doctrine moves. Gate tests read spine; detail tests read exact routed files.
   Extend reference discovery/Contents, semantic pointers and installation checks.
   Avoid a catch-all reconstructed string that can hide missing/incorrect routes.
4. **Probe and review.** Run the focused counterexample matrix below, then independent
   review of conservation and actual mutation effects. Fix findings and freeze source.
5. **Integrate.** One serial owner `npm run test:all` on the final reviewed source,
   genuine candidate PR checks and normal merge under the repository policy. Release
   packaging is a separate next decision; do not change 1.94.0 in this planning slice.

The report/packet owner is recovery_audit. Parent supplies independent source review;
implementation ownership is not dispatched before acceptance. All file leases are
advisory locally, not an enforced cross-machine lock.

## Focused counterexamples

- Delete one stage detail, route to a sibling, or duplicate a default stage id.
- Remove a non-gate obligation from detail while every spine gate remains unchanged.
- Shorten a multi-paragraph gate after its first sentence; change a gate type/name.
- Keep an old surface-class link syntactically live but pointing only at an unrelated
  gate paragraph; remove its actual destination or change its heading.
- Enter/resume stages0,3,5,7,10, a wave's5–8 sequence and an approved short path; each
  route names its own detail, not all details or a guessed stage from another profile.
- Use a custom three-stage profile with numeric ids overlapping the default; retain
  custom gates and kernel obligations, not the default semantics for those numbers.
- Copy only the skill directory to isolation and resolve all runtime references.
- Remove Read hooks/ledger: doctrine remains unmeasured; add a ledger read: unattested.
- Mutate relocated prose at the actual path and demonstrate the intended diagnostic;
  an old selector that no longer lands must report broken, never silently pass.

These are source/helper fixture expectations. A native-host quality claim additionally
needs frozen realistic tasks, baseline/current same model/settings, selected-read
traces and final artifacts judged independently. Test routing correctness, task result
correctness and total token usage separately; absent transcripts are NOT_RUN. A
simulated route table is not a replacement for those observations.

## Source acceptance requested

Parent review should decide the conservative layout, the exact routing contract and
how to handle the named pre-existing UX contradiction. No code is awaiting approval
in this branch. Next action after acceptance: freeze old→new mapping and small
implementation task list; preserve all gates, then prove targeted loss controls.
