# Carry-over ledger — `audit-followup`

Appended the moment something is deferred, dropped or left half-done. Read in full at
stage 10 of every module. The count is printed beside every gate verdict.

| # | Row | Raised at | Home | Status |
|---|---|---|---|---|
| 1 | ~~Seven releases (v1.17.0–v1.23.0)~~ — **re-measured at the moment of use, not inherited**: **ten consecutive releases, `v1.16.0` through `v1.23.0`**, shipped without a pipeline run, a brief, a spec or a run stamp. The original row was a filtered subset that had lost its filter (rule 16), and it understated both the count and the boundary. Command: resolve `git tag -l 'v1.*'` to SHAs and compare against the `| date | topic | sha |` rows of `docs/superpowers/retro.md` | stage 0, corrected in **M3** | REQ-007 / **M3** | open |
| 2 | The shipped doctrine is ~97.5k tokens over 30 reference files, and `SKILL.md`'s frontmatter description sits at 1015 of the 1024-character limit — so M7 must displace text to add a companion, not append it | stage 0 | **M7** carries the displacement decision; the growth rule is **M6** | open |
| 3 | `docs/DOCMAP.md` records no register for open questions (`none`), so a question raised mid-run has nowhere to live but this ledger | stage 0 | — | open — accepted for this program |
| 4 | Rule 21's stamp-first ordering reached `references/retrospective.md` only; every other surface that stated it still taught the deadlock | **M1**, by R-003's sweep | REQ-013 / **M8** | **closed in M8** — every surface corrected, and a guard now compares the order rather than the citation |
| 5 | The installed `graphify` skill is behind its package — the CLI warns `skill is from graphify 0.9.34, package is 0.9.36`. Stage 9's refresh runs through the agent-side `/graphify` skill (the CLI has no build, query, affected or god-nodes subcommand — verified with `graphify --help`), so a stale skill is a stale refresh | **M1** stage 9 | run `graphify install` before the first refresh | **resolved in M1** — see below |
| 6 | `evals/RESULTS.md` now states the blind/self-observed split honestly, but the underlying fact is unchanged: **zero blind runs on zero of three models.** The skill's behavioural evidence is still one self-check by its author | **M1** | needs fresh sessions per model — not schedulable inside this program | open — **printed, not fixed** |
| 7 | `CLAUDE.md:56` says *"The stage list lives on nine surfaces"* and then enumerates three mechanical plus seven human — ten surfaces across nine files. Same class as `four-way`, different fact, and out of M8's subject | **M8**, by the count sweep the PR review triggered | **M2** | **closed in M2** — deleted rather than gated: a count of an enumeration inside one sentence is not computable from outside it, and the line now says so |
| 9 | ~~The M8 graph refresh dropped **9 nodes** to id collisions~~ — **closed in M2's refresh**: the `source_file` convention was stated once, verbatim and absolute, in the dispatch prompt. Result measured: **0 collisions** (one fuzzy dedup) against nine lost nodes before. The fix was in the instruction, not the tool | The M8 graph refresh dropped 9 nodes to id collisions: the two extraction chunks were given different `source_file` conventions (absolute in one prompt, relative in the other), so graphify minted two ids for one entity and kept one. Reported by the tool, not caught by a check | **M8** stage 9 | one `source_file` convention stated once in the dispatch prompt | open |
| 8 | The PR review found three issues this run's own gates did not, one of them a **proven false-negative path** in the guard being shipped. The reviewer is not in the pipeline's stage list; it ran because the repository has a bot on PRs, not because a stage asked for it | **M8** stage 7 | the doctrine has no stage that dispatches an independent reviewer of a *doctrine* change — stage 5's review loop covers code | open — **needs a home** |
| 10 | The graph's **shrink guard** refused a refresh that took it 864 → 839 nodes, and the first instinct was to explain the drop plausibly (*"re-extraction produced a tighter fragment"*) rather than verify it. Verified instead: **99 nodes lost, every one from a file re-extracted this run; zero from untouched files.** Only then was `force` a decision on evidence rather than a way past a guard — which is exactly what the guard's own message asks for | **M7** stage 9 | none needed; recorded because the near-miss is the lesson (R-006 from the other side: a plausible explanation almost passed for a verification) | **closed by measurement** |

## Notes that are not rows

**Row 5 was fixed rather than carried.** It was raised and closed inside M1: the check
is one command and the fix is one command, so carrying it would have been a TODO with a
better name.

**Row 6 is the honest ceiling of this program.** Everything M1–M8 does is structural. No
amount of it produces behavioural evidence, and saying so beside the green is the point
of the row.
