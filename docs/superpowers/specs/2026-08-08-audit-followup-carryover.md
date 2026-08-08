# Carry-over ledger — `audit-followup`

Appended the moment something is deferred, dropped or left half-done. Read in full at
stage 10 of every module. The count is printed beside every gate verdict.

| # | Row | Raised at | Home | Status |
|---|---|---|---|---|
| 1 | Seven releases (v1.17.0–v1.23.0) shipped without a pipeline run, a brief, a spec or a run stamp | stage 0 | REQ-007 / **M3** | open |
| 2 | The shipped doctrine is ~97.5k tokens over 30 reference files, and `SKILL.md`'s frontmatter description sits at 1015 of the 1024-character limit — so M7 must displace text to add a companion, not append it | stage 0 | **M7** carries the displacement decision; the growth rule is **M6** | open |
| 3 | `docs/DOCMAP.md` records no register for open questions (`none`), so a question raised mid-run has nowhere to live but this ledger | stage 0 | — | open — accepted for this program |
| 4 | Rule 21's stamp-first ordering reached `references/retrospective.md` only; eight sibling surfaces still teach the deadlock | **M1**, by R-003's sweep | REQ-013 / **M8** | open |
| 5 | The installed `graphify` skill is behind its package — the CLI warns `skill is from graphify 0.9.34, package is 0.9.36`. Stage 9's refresh runs through the agent-side `/graphify` skill (the CLI has no build, query, affected or god-nodes subcommand — verified with `graphify --help`), so a stale skill is a stale refresh | **M1** stage 9 | run `graphify install` before the first refresh | **resolved in M1** — see below |
| 6 | `evals/RESULTS.md` now states the blind/self-observed split honestly, but the underlying fact is unchanged: **zero blind runs on zero of three models.** The skill's behavioural evidence is still one self-check by its author | **M1** | needs fresh sessions per model — not schedulable inside this program | open — **printed, not fixed** |

## Notes that are not rows

**Row 5 was fixed rather than carried.** It was raised and closed inside M1: the check
is one command and the fix is one command, so carrying it would have been a TODO with a
better name.

**Row 6 is the honest ceiling of this program.** Everything M1–M8 does is structural. No
amount of it produces behavioural evidence, and saying so beside the green is the point
of the row.
