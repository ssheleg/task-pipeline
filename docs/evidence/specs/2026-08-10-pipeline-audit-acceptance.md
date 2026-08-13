# Acceptance — the pipeline audit and the four modules it produced

Closed 2026-08-10. Brief: [`2026-08-10-pipeline-audit-brief.md`](2026-08-10-pipeline-audit-brief.md).

## Ladder walk (runs before the table)

Walked bottom-up per REQ: decision → doctrine section → contract and its failure
behaviour → change → executed probe → surface. Ordered by seam, not by file.

| Seam | What the walk found | Where it went |
|---|---|---|
| doctrine → guard | The short-path check read a **paragraph** while the bullet it parses carries a fenced block; it stopped three lines short of the glyph and passed in silence | fixed in P2, unit stated in the code |
| guard → its own input | The same check then matched the **fence's own backtick** and accused the clean tree | fixed in P2 |
| doctrine → guard | Five fence scans across four modules matched ` ``` ` + newline; a ```json block upstream made every later fence pair with the wrong delimiter, so P4's example check never read the block it exists for | fixed in P4, all five scans, P1–P3 probes re-run |
| matrix → stage | `chrome-devtools` pointed at **stages 5–6** with stage 5 never naming it — true since the row was added | fixed in P3, found by the new guard on its first run |
| probe → check | Three probes were wrong before the guard was: one removed 1 of 3 `touch:` lines, one planted in a **released** CHANGELOG section, one deleted the SHOUTED spelling of a track and left the lowercase one | all three repaired; recorded in the retro |
| gate → next command | `npm test \| head && git commit` read `head`'s status; a commit landed over a red validator | amended, R-004 stamped |
| **absence** | R-005's independent reader **did not run**: the review app reported `skipping` on every PR of this programme | new REQ row below, and a live instance of B-003 |

## Coverage

| REQ | Status | Evidence |
|---|---|---|
| REQ-011 header block at task start | verified | `references/progress.md` → *The header block*; guard P1-G1 compares its field set with `stages.md` both ways, probed |
| REQ-012 one-line iteration close | verified | `references/progress.md` → *The iteration line*; `continuity.md` restates it and requires a `B-NNN` |
| REQ-013 rail computed, never eleven | verified | guard P1-G3 requires *"come from the project's `pipeline.json`"* and *"carries no stage count of its own"*; probed by softening the clause to "the eleven stages" |
| REQ-015 `.task-pipeline/run.md` seeded at stage 0 | verified | `templates/run.md`; stage 0 bullet + gate criterion; guard P1-G4 compares declared vs shown vs read, three ways, probed |
| REQ-014 review-round cap | verified | `loop-guard.md` → *The review loop*; guard P2-G1 computes the number from that file and requires it in `stages.md`; three plants |
| REQ-016 short-path triage | verified | `stages.md` phase 1d; guard P2-G2 requires the skip glyph to be in `progress.md`'s legend, probed with `※` |
| REQ-017 exposure example matches its print | verified | `references/exposure.md`; guard P2-G3 derives the vocabulary from the print statement and rejects a digit in the example; two plants |
| REQ-018 COPY and VISUAL tracks at stage 3 | verified | `stages.md` stage 3 + its gate; guard P3-G2 requires all three tracks and their owners, probed by deleting one and by orphaning another |
| REQ-019 matrix and preflight name them | verified | `companion-skills.md` matrix + preflight; the existing both-directions guard passes; guard P3-G1 additionally requires the stage to name the companion |
| REQ-020 `retro.publish`, opt-in, printed first | verified | `retrospective.md` → *Publishing the insight*; `pipeline.schema.json` → `retro.publish`; guard P4-G3, both directions plus the stage, probed |
| REQ-021 redaction is enumerated and checkable | verified | five numbered rules, count computed from the items; guard P4-G1; P4-G2 checks the doctrine's own worked issue against rules 1 and 2 — three plants |
| REQ-022 audit findings on the board | verified | `docs/superpowers/backlog.md` — B-025…B-032 added at stage 0, all eight in *Closed* with their release |
| **REQ-023** *(new, from the ladder walk)* the independent reader R-005 requires | **partial** | The review app reported `skipping` on #20, #21, #22, #23. Every change here adds or widens a check, which is exactly R-005's trigger. **No independent reader ran.** Tracked as a live instance of board row B-003 |

## Disclosures

```
abstained: 1 (REQ-023 — no independent reader observed)
unlooked:  0
```

**REQ-023 is reported, not fixed.** R-006 exists for this sentence: naming the gap is
honest and is not closing it. The reader R-005 asks for is dispatched by "the repository
happening to run a bot on PRs" — its own retirement condition says so — and on this
programme the bot declined. Four modules of guard changes went in with the author's own
probes as their only reading, which is the precise limit R-005 was written to name.

## What this programme did not touch

- The 99 `never` rows. A person opens the product; no module here can.
- Blind eval runs (B-002) — a fresh session per query per model, a separate act.
- The code graph (B-007) — needs a key this session does not have. Still stated.
