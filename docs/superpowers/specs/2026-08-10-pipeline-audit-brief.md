# Brief — the audit, the progress print, the design/copy tracks, and retro as issues

Locked at stage 0 on 2026-08-10. Operator: sshlg. Standing authorization for the
programme; the outward acts (PR merge, tag, release, opening an issue in another
repository) keep their own gates.

## The request, in one line

Audit what shipped, what the docs claim, and which gates loop — then close the four
gaps that audit names: the pipeline never says which pipeline it is on, its review
loop has no ceiling, it routes UI work to `super-ux` and to nothing that owns how the
product **sounds** or **looks**, and every lesson it learns dies in one repository.

## Source ledger (stage 0 harvest)

| Source | What it gave |
|---|---|
| `npm test` (live) | 99 shipped REQ · **99 at `Human: never`** · `unlooked: 0` · 188 guards · claim registry 9 classes, 6 dormant |
| `docs/superpowers/retro.md` | six standing instructions read in full (R-001…R-006, none retired); 24 run stamps; review-round counts **10, 10, 8, 4, 3** |
| `docs/superpowers/backlog.md` | 13 open rows, top priority 6 — B-001 (frontmatter 1015/1024), B-002 (zero blind evals), B-003 (reviewer not in the stage list) |
| `references/loop-guard.md` | caps: 5 fix rounds/task, 2 stage re-entries, 3 module passes. **No cap for a stage-7 review round.** Ledger `.task-pipeline/run.md` required |
| `.task-pipeline/` | holds `build/` only — **`run.md` has never been written by any run** |
| `references/companion-skills.md` | matrix names 6 super-ux surfaces; super-ux ships 8 skills and **15 commands** |
| repo grep | `sheleg-design` — **1 occurrence**, `README.md:861`, a name in a family list. `copywriting` — **0** |
| `references/exposure.md:40` | worked example prints `31 releases since the last human confirmation`; `test/validate.py:3236` prints `10 releases carry one` |
| `evals/RESULTS.md` | suite authored, 1 self-observed run, **0 blind runs on 0 of 3 models** |
| `SKILL.md` frontmatter | description **1015 of 1024** characters — 9 left |
| code graph | present, 839 nodes, stale (board row B-007 — stated, not closed) |
| checkout | clean, `origin/main` synced, `v1.33.0` |

## Decisions taken at the grill

| # | Question | Answer |
|---|---|---|
| D1 | progress print shape | **rail + counter** — a header block at task start, a one-liner every iteration |
| D2 | retro → issue authorization | **opt-in in `pipeline.json`, default off**; the full text is printed, then the issue is opened without re-asking. Silence arms nothing, exactly as with deploy |
| D3 | design/copy routing depth | **full tracks in stage 3** — what it does / how it sounds / how it looks, each with gate criteria and a recorded refusal |
| D4 | which gate defects to fix | review-round cap **and** the stage ledger **and** the short path for small changes |
| D5 | branch policy | this repo's `CLAUDE.md`: structural → branch + PR + its own minor. Not re-asked; it is written down |

## The correction I am making to the request, out loud

The request says the agent should print progress *"каждую итерацию"*. An iteration is
already defined ([`continuity.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/continuity.md)
→ *What one iteration means*) as **one item taken to its gate** — not one agent turn.
Printing per turn would put a progress bar above every tool call and teach the operator
to skip the block that matters. What ships prints on the two boundaries that are real:
**task start** and **iteration close**.

Second correction: the rail must not hardcode eleven stages. The eleven in
`pipeline.example.json` are this plugin's *example*; a host project replaces them
(`SKILL.md` → *Bring your own skills*). A progress bar that says `5/10` in a project
with six stages is the false-success class this repository removes.

## REQ table (frozen — adding is free, removing needs the operator)

| REQ | Requirement | Verified by | Module |
|---|---|---|---|
| REQ-011 | A **header block** at task start: skill + version, programme, module *N of M*, the stage rail, the ratio, the gate type, board id, carry-over, exposure | doctrine + guard on the format contract | P1 |
| REQ-012 | A **one-line** print at every iteration close, citing a `B-NNN` rather than a description | doctrine + guard | P1 |
| REQ-013 | The rail's stage set is **computed from the project's `pipeline.json`**, never a literal eleven | guard: the progress doctrine states no stage count of its own | P1 |
| REQ-014 | Stage 7's review loop carries a **declared cap**; past it the run enters loop-guard's break protocol instead of another round | `loop-guard.md` + `stages.md` state the same cap; guard both | P2 |
| REQ-015 | `.task-pipeline/run.md` is **created at stage 0** and appended by every repeating pass — the ledger loop-guard already requires | doctrine + template + the stage-0 gate criterion | P2 |
| REQ-016 | Stage 0 **measures the change** and proposes the short path when the work is below the pipeline's own boundary | `grill.md` sweep row + `stages.md`; the measurement is a command, not a feeling | P2 |
| REQ-017 | `exposure.md`'s worked example **matches what ships** | guard comparing the doctrine's example to the print statement | P2 |
| REQ-018 | Stage 3 gains a **COPY track** (copywriting / brand pack) and a **VISUAL track** (sheleg-design), each with gate criteria and a refusal phrase recorded out loud | `stages.md` + `spec.md` gate text; guard | P3 |
| REQ-019 | The companion matrix **and** the preflight name `copywriting`, `brand-voice`, `vision` and `sheleg-design` | the existing matrix ↔ preflight guard, both directions | P3 |
| REQ-020 | Retro insights publish as **GitHub issues** under `retro.publish`, default off, the full text printed before the issue is opened | doctrine + schema + template | P4 |
| REQ-021 | **Redaction is an enumerated, checkable rule set** — insight only: no host paths, no operator or project names, no code, no customer data | doctrine carrying the list; guard that the list is enumerated rather than promised | P4 |
| REQ-022 | Every finding of this audit is a **board row with computed priority** | the board, both directions against this brief | P0 |

**Definition of done, every module** (a gate criterion, not a REQ row): each new guard
is watched failing against a planted defect (`npm run test:negatives`), R-005's
independent reader runs before merge, and R-006 is honoured — a gap reported is said to
be reported, not claimed as fixed.

## Module map (stage 2)

Walking skeleton first: the audit's findings need somewhere to live before anything is
built on top of them.

| # | Module | REQ | Ships as |
|---|---|---|---|
| **P0** | **the audit's findings onto the board** — rows with their inputs, so the rest of this programme is worked from a measured queue | REQ-022 | on `main` |
| P1 | **the progress print** — header, iteration line, the rail computed from the project's own stages | REQ-011·REQ-012·REQ-013 | v1.34.0 |
| P2 | **the gate fixes** — the review cap, the run ledger, the short path, the drifted example | REQ-014·REQ-015·REQ-016·REQ-017 | v1.35.0 |
| P3 | **the design and copy tracks** — stage 3 grows two lanes beside the UX one | REQ-018·REQ-019 | v1.36.0 |
| P4 | **retro as issues** — the skill learns from every project that runs it | REQ-020·REQ-021 | v1.37.0 |

## Out of scope

- **Closing the 99 `never` rows.** That is a person opening the product, and no module
  here can do it. The exposure line already says so on every run.
- **Running the blind evals** (B-002). It needs a fresh session per query per model —
  a separate act, not a module of this programme.
- **Rebuilding the code graph** (B-007). Needs a key this session does not have; it
  stays a board row and stays stated.
- **Making the retro publisher work without `gh`.** Where the CLI is absent the module
  prints the issue body and says it did not open it — the honest degradation, not a
  second transport.
