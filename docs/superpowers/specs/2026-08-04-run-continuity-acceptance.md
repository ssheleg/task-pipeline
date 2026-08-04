# Acceptance — run continuity

**Run:** `run-continuity` · 2026-08-04 · **13 REQ** · brief:
[`…-brief.md`](2026-08-04-run-continuity-brief.md) · spec:
[`…-design.md`](2026-08-04-run-continuity-design.md)

**Carry-over ledger: 4 rows — 2 resolved, 2 open with a named home, 0 unresolved.**
Printed here beside the verdict on purpose: *green* must never be read as
*everything is finished*.

## Contents

- The ladder walk
- Coverage
- What the ladder found that the REQ table could not
- Honest gaps

## The ladder walk

Walked bottom-up per REQ — decision → spec section → contract → task → change →
executed check → surface. Two absences surfaced and both became REQ rows **before**
this table was written, which is the point of walking first:

- **REQ-012** (stage 1) — `templates/carryover.md` shipped a relative link that
  breaks the moment the template is seeded where its own doctrine says to seed it.
  Found by seeding it. The existing link checker was green throughout, because it
  resolves links from the file's *home* and the defect only exists at the
  *destination*.
- **REQ-013** (stage 2) — a fixed-interval loop firing into a `manual` gate is a
  nag, and a nagged operator stops reading. Found by running the loop this change
  was adding.

## Coverage

| REQ | Verdict | Evidence — the artefact, not the document describing it |
|---|---|---|
| 001 | verified | `definitions.run` present; `loop.mode` enum `['off','interval']`; **no `contextBudget` key**, and the schema's own `description` says why. Guard G1 watched failing on a stripped example |
| 002 | verified | `references/continuity.md`, 206 lines. Reachability, README-map and portability-manifest guards all green — each already had a negative self-test |
| 003 | verified | `SKILL.md` (3 mentions), `grill.md`, `templates/brief.md` each name it. Guard G2 watched failing |
| 004 | verified | `build.md` and `stages.md` name it; `build.md`'s *Continuous execution* paragraph keeps its full force and gained a scope sentence. Same guard G2 |
| 005 | verified | The evidence clause present after whitespace normalisation. Negative test G3a watched removing it and the validator rejecting |
| 006 | verified | `Claude Code only` present; negative test G3b watched failing |
| 007 | verified | 68 `Negative self-test` steps; `MIN_EXPECTED = 68`; `npm run test:all` → `PASS: all 68 guards provably reject their planted defect` |
| 008 | verified | Four-way sync at `1.11.0`; CHANGELOG `## v1.11.0`; guard counts recomputed from the workflow by the compute-never-restate guard, **which fired on SKILL-CARD.md and evals/RESULTS.md rather than being trusted** |
| 009 | **verified by eye** | `~/.claude/CLAUDE.md:85`, 18 lines inserted, 256 → 274. **No guard in this repository can see that file.** Stated, not dressed up as the other twelve |
| 010 | verified | `pipeline.example.json` carries `run.loop.mode: "off"` explicitly. G1 rejects its removal |
| 011 | verified | `docs/DOCMAP.md` gained the *change to the config contract* row, born from walking the matrix and finding it absent |
| 012 | verified | Zero relative links remain in any template; `adr.md`, `carryover.md`, `routing-rule.md` fixed. Guard G4 watched failing on a planted link |
| 013 | verified | `continuity.md` → *Parked at a manual gate*; applied twice in this run — the loop was cancelled on parking at stage 2 and at stage 3 |

**13 of 13 accounted for. 12 by a check seen failing once; 1 by eye, and said so.**

## What the ladder found that the REQ table could not

**The spec asked for something impossible, and measuring caught it.** G4's first
shape required a template's relative links to resolve *from the destination*. They
cannot: the same file also lives in `templates/`, where this repository's link
checker resolves them from **there**. One link, two required bases, no value
satisfying both. Building it as specified would have produced a guard that could
never go green — or, worse, a link "fixed" for the destination and quietly broken
at home.

The rule that replaced it is stronger and already had a precedent here: **a
document that travels carries no relative links at all**, the same requirement the
Cursor rule has always had, for the same reason.

## Honest gaps

- **The code graph is stale** (carry-over row 3). Last built 2026-08-01; this run
  changed four files it indexes. graphify's semantic pass needs subagent dispatch,
  which this session was instructed not to use. Not silently skipped: the next
  run's stage-0 harvest must treat `graphify-out/` as a false premise until
  refreshed.
- **The wiki is four releases behind** (carry-over row 4), deferred to protect the
  context stage 10 needed.
- **`Claude Code Review` never returned** on the pull request — pending with zero
  duration past ten minutes. The blocking gate (`validate`) passed twice on the
  tagged commit. Recorded rather than waited out, and recorded rather than
  ignored.
- **Merge and tag are blocked by the harness safety classifier**, correctly: both
  are outward. The operator's authorization exists; the mechanical permission does
  not.
