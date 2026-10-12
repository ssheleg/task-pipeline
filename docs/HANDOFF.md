# Start here — task-pipeline

Snapshot: 2026-10-12. Released: **v1.92.0** (npm `task-pipeline-skill`, 2026-10-11), wave mode.
Released: **v1.93.2** (v1.93.0's payload; the v1.93.0 and v1.93.1 tags published nothing — see CHANGELOG).
In review: **v1.93.3** on `fix/w2-recert` — see the next section.
[Verification](evidence/verification.md) · [board](evidence/backlog.md) · [CHANGELOG](../CHANGELOG.md).

## In flight — v1.93.3 (branch `fix/w2-recert`), a patch to wave 2

Findings from a re-certification reading of v1.93.2 and an independent observer
(CHANGELOG `v1.93.3`, verification section *Shipped state — v1.93.3*):

- The seven wave-2 commit references that a clone cannot follow are backticked again and
  declared in `docs/evidence/retro.md` (`docgate:known-dead`, reason and
  `git fetch origin pull/109/head` beside it).
- `stage_checkpoint.py handoff` keys a retry on memory events only, so a `gate:` line no
  longer turns a retry into a replacing offer.
- R13 gained `scripts/backlog_sources.py` + `test/backlog_sources_test.py`; R16 gained
  `test/release_approval_test.py`. CI's validate job now also runs these two and
  `memory_nudge_test.py`, which was in `npm test` but not in CI.

**Next task:** after the PR merges with checks green, push the `v1.93.3` tag and watch
`release.yml`. The approval mode is not declared in `pipeline.json`, and on 2026-10-12
`gh api repos/ssheleg/task-pipeline/environments/release` returned 404, so no reviewer
gate exists (`references/deploy-targets.md`). Then the hub re-pins 1.93.3 instead of
1.93.2 in wave 5.

## Wave 2 (shipped as v1.93.2; its branch is deleted, its commits are under `pull/109/head`)

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
  in `test/negatives/` (the hub plan said `test/negatives.json`; each check is a shell
  script, so it ships as a directory, every file byte-checked against the YAML-parsed
  `run` value it came from); `validate.yml` went from 507,836 to 12,181 bytes; the `negatives`
  job runs `test/negatives.py --shard N/8` on an eight-value matrix. All eight shards
  passed locally on `941bed8`, pre-squash (438 plants rejected, 15 property checks printed, none
  dormant). On CI the eight shards took 3m29s–6m45s (row `R08-ci`), and B-100 is
  closed.
- **R09 budget.** Description 909 → 890 chars; body 4736 → 4646 of 4750 tokens. B-120
  closed with the auditor's reading.
- **R10 ledgers.** The verification headers read "released"; the merged branches
  `feat/wave-mode` and `fix/no-stamp-1912` are deleted.
- **R11** Observatory checkpoint/handoff and the memory nudge · **R13**
  `backlog-sources.json` · **R14** namespaced packet id · **R15** Fabric contract
  fixture · **R16** release approval mode.

PR [#109](https://github.com/ssheleg/task-pipeline/pull/109): run `38242485458` green —
the slowest shard 6m45s and the whole run 6m50s, where the one job had taken 90–111 min.
Verification row `R08-ci` holds the numbers. B-100 is closed with them.

The hub (ssheleg/sshlg-skills) re-pins task-pipeline in wave 5, which closes B-160. The family rows B-154 and HK-05 live in the
sshlg-skills board and close there, at the wave-5 re-pin.

The previous page (the 2026-09-07 Sherlock audit branch) is history:
[that revision](https://github.com/ssheleg/task-pipeline/blob/aea2e14561b3ed3a20ce05fcfa7c08e7b9ae74ab/docs/HANDOFF.md).
