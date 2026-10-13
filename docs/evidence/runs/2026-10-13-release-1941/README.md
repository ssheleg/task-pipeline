# Release repair candidate: v1.94.1

Status: AUTHORING; no publication or local full-gate acceptance.

## Objective and authority

The operator authorized autonomous completion of the family waves. The parent
assigned this bounded owner repair after release run 38386280311 failed. Preserve
the immutable failed v1.94.0 tag; prepare v1.94.1 with truthful missing-run-stamp
records. No fabricated stage-10 stamp. No new skill behavior or workflow changes.
The inherited model and act-specific authority remain unchanged.

## Source ledger and contradiction

- Base: [accepted main](https://github.com/ssheleg/task-pipeline/commit/78c42124db910c56e74c8fbd524bdc9a4f8fb6c9).
- [Failed release](https://github.com/ssheleg/task-pipeline/actions/runs/38386280311):
  release failed, publish skipped; structural diagnostic names missing v1.94.0
  in the retro gap declarations. The historical tag remains unchanged.
- CLAUDE.md version invariant names package, marketplace, plugin, SKILL-CARD and
  the top CHANGELOG heading. These are the five surfaces, despite the older
  CONTRIBUTING release shorthand saying four.
- CONTRIBUTING.md release section says npm test. The stricter pipeline.json
  stage-7 condition and active retro R-010 require npm run test:all against the
  locally tagged source before pushing a release tag. Branch CI is not a waiver.
- test/validate.py release-gap section reads actual Git tags and bold declarations
  under `Releases that carry no stamp`. An ordinary prose mention is insufficient.
- docs/DOCMAP.md propagation matrix: metadata/changelog/SKILL-CARD and owner handoff;
  Cursor rules and skill payload behavior remain byte-identical in this repair.
- Shared family brand source: sshlg-skills docs/brand voice, terminology, facts and
  Release note channel. Owner release facts below are direct Git/Actions evidence.

Contradictions: prior pre-tag admission inferred npm test plus PR CI was enough.
That inference conflicts with pipeline.json and R-010. The earlier aborted local
full run and successful branch jobs remain historical, not exact-tag acceptance.

## Requirements and bounded plan

| ID | Contract | Acceptance |
|---|---|---|
| RR1 | Failed v1.94.0 tag preserved | remote annotated object/peeled target unchanged |
| RR2 | v1.94.1 synchronized | validator plus exact five-surface values |
| RR3 | Missing stamp remains explicit | bold declarations for both versions; no new run-stamp row |
| RR4 | Real tag context checked | local annotated candidate exists before structural run; no release-gap unlooked |
| RR5 | No skill behavior drift | published non-metadata payload hashes unchanged |
| RR6 | Handoff is bounded | draft PR, focused receipts, full/tag/publish/install acceptance pending |

1. Capture actual failed release and reproduce the structural defect on the base.
2. Add the missing-gap declaration and patch metadata/changelog; preserve historical
   sections, standing rules, stamp rows and all executable/skill doctrine bytes.
3. Commit candidate, create an annotated local v1.94.1 tag without pushing, then
   validate. Record actual exit codes and disclosures; probe each declaration omission.
4. Push only the branch and open a draft PR for independent audit. No hosted full
   dispatch or local broad suite in this disk-constrained authoring slice.
5. After normal integration and safe disk admission, the release owner must test
   the accepted locally tagged source with npm run test:all before any tag push.

## Unpublished candidate-tag lifecycle

The author owns only the new local candidate v1.94.1 tag, never v1.94.0. Its object
and target are recorded after creation. It is not pushed with the branch. Normal
squash integration changes the commit identity. Before final release, verify remote
v1.94.1 is absent and local candidate still equals the recorded owned object; only
that unpublished candidate may be removed and recreated annotated at the accepted
merge commit. Then rerun the exact-tag full gate. If either ref differs or any
remote v1.94.1 exists, stop this procedure and reconcile without force or deletion.
The candidate structural pass is not a full gate or final-merge acceptance.

## Exact next task

Independent audit of the frozen metadata/gap diff and focused receipts, followed
by the serial full gate when disk permits. No tag push is authorized by this packet.
