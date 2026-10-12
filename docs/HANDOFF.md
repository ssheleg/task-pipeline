# Start here — task-pipeline

Snapshot: 2026-10-12. Released: **v1.92.0** (npm `task-pipeline-skill`, 2026-10-11), wave mode.
In flight: **v1.93.0** on `w2/hygiene-continuity`.
[Verification](evidence/verification.md) · [board](evidence/backlog.md) · [CHANGELOG](../CHANGELOG.md).

## In flight — integration wave 2 (branch `w2/hygiene-continuity`)

Driven by the sshlg-skills waves run: plan
[`docs/evidence/plans/2026-10-11-integration-waves.md`](https://github.com/ssheleg/sshlg-skills/blob/waves/2026-10-11-integration/docs/evidence/plans/2026-10-11-integration-waves.md)
(Wave 2, R07–R16).

Every wave-2 packet is committed on this branch, versioned **1.93.0** (CHANGELOG
section `v1.93.0`, verification section *Shipped state — v1.93.0*, rows at `never`).
Not tagged, not published: the release follows the PR's merge.

- **R07 test temp residue.** `tp-b80` (`test/validate.py`), `tp-stage-ckpt` and 15 files
  with bare `mkdtemp` clean up after themselves. A validator check now refuses a test
  file that makes temp state with no cleanup (plant `test/negatives/453-…`); writing it
  found and fixed two leaks in `test/validate.py` itself.
- **R08 / HK-05 / #91.** The 433 negative self-tests and 15 property checks are files
  in `test/negatives/`; `validate.yml` went from 507,836 to 12,181 bytes; the `negatives`
  job runs `test/negatives.py --shard N/8` on an eight-value matrix. All eight shards
  passed locally on `941bed8` (438 plants rejected, 15 property checks printed, none
  dormant). The CI wall clock per shard goes into the verification row `R08-ci` and
  closes board row B-100.
- **R09 budget.** Description 909 → 890 chars; body 4736 → 4646 of 4750 tokens. B-120
  closed with the auditor's reading.
- **R10 ledgers.** The verification headers read "released"; the merged branches
  `feat/wave-mode` and `fix/no-stamp-1912` are deleted.
- **R11** Observatory checkpoint/handoff and the memory nudge · **R13**
  `backlog-sources.json` · **R14** namespaced packet id · **R15** Fabric contract
  fixture · **R16** release approval mode.

**Next task:** read the PR's CI by run id, write each shard's duration into
`docs/evidence/verification.md` (`R08-ci`), close B-100 with them, then merge and release
1.93.0 per `CLAUDE.md` → *Deploy / release*. The family rows B-154 and HK-05 live in the
sshlg-skills board and close there, at the wave-5 re-pin, citing this branch.

The previous page (the 2026-09-07 Sherlock audit branch) is history:
[that revision](https://github.com/ssheleg/task-pipeline/blob/aea2e14561b3ed3a20ce05fcfa7c08e7b9ae74ab/docs/HANDOFF.md).
