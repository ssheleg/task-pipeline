# Start here — task-pipeline

Snapshot: 2026-10-12. Released: **v1.92.0** (npm `task-pipeline-skill`, 2026-10-11), wave mode.
[Verification](evidence/verification.md) · [board](evidence/backlog.md) · [CHANGELOG](../CHANGELOG.md).

## In flight — integration wave 2 (branch `w2/hygiene-continuity`)

Driven by the sshlg-skills waves run: plan
[`docs/evidence/plans/2026-10-11-integration-waves.md`](https://github.com/ssheleg/sshlg-skills/blob/waves/2026-10-11-integration/docs/evidence/plans/2026-10-11-integration-waves.md)
(Wave 2, R07–R16).

Done on this branch:
- **R07 test temp residue.** `tp-b80` (`test/validate.py`), `tp-stage-ckpt` and 15 files
  with bare `mkdtemp` now clean up after themselves.
- **R09 budget.** The description went from 909 to 890 chars, and the body from 4736 to
  4619 tokens.
- **R10 ledgers.**
  - The verification headers read "released".
  - The merged branches `feat/wave-mode` and `fix/no-stamp-1912` are deleted.
  - This page is current.

Open in this wave:
- **R08 / HK-05 / #91.** Move the 448 negative and property steps out of
  `validate.yml` (507,836 of 512,000 bytes) into `test/negatives/`, then shard them in
  a matrix.
  - At least 10 checks in `test/validate.py` read the workflow.
  - 12 plants use its text as their payload.
  - This is its own careful packet.
- **R11** Observatory checkpoint/handoff.
- **R13** `backlog-sources.json`.
- **R14** namespaced packet id.
- **R15** Fabric contract fixture.
- **R16** release approval mode.

The previous page (the 2026-09-07 Sherlock audit branch) is history:
[that revision](https://github.com/ssheleg/task-pipeline/blob/aea2e14561b3ed3a20ce05fcfa7c08e7b9ae74ab/docs/HANDOFF.md).
