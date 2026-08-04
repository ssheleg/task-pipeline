# Task brief — run continuity

**Run:** `run-continuity` · 2026-08-04 · model: Opus 5 (top tier available,
confirmed at preflight, no per-stage overrides)

Two doctrine items the pipeline is missing, both about **how a run keeps going**:
the loop that walks a task list without asking permission between items, and the
rule for what happens as the context window runs out.

## Contents

- Knowledge sources
- Documentation
- Scope
- Requirements (the REQ spine)
- Users & context
- Decisions locked
- Autonomy
- Done-criteria
- Open assumptions / risks

## Knowledge sources (the phase-1 harvest — written BEFORE the first question)

| Source | What it says about this task | Fresh? |
|---|---|---|
| `CLAUDE.md` (repo) | Nine-surface stage list, four-way version sync, `npm test` runs bash, the propagation obligations | current |
| `~/.claude/CLAUDE.md` (global) | Routing rule sends repo-changing work through the pipeline; ops steps are the agent's own Definition of Done; production-grade bar | current |
| `docs/DOCMAP.md` | Registers, SSOT table, **propagation matrix**, gates. The matrix has rows for a new document/rule/guard and for a user-visible capability | current — but see REQ-011 |
| `docs/superpowers/retro.md` | R-001 and R-002 in force. Recent log's repeated lesson: *declaring a thing cross-cutting does not distribute it*; a command documented in 13 files that behaves differently when run | current |
| `references/build.md:17–19` | **Already carries half of item 2** — *"Continuous execution: don't check in between tasks… 'Should I continue?' between tasks is noise"* — unconditional, stage-5-only, invisible at preflight and in the config | stale in reach, not in content |
| `references/grill.md` → autonomy sweep | Fifteen rows; **no row for run pacing or for the context budget** | incomplete for this task |
| `references/hooks.md` | Precedent for a harness-specific mechanism: `PreCompact` / `PostCompact` exist, and the file states the Claude-Code-only limit out loud | current — the pattern to copy |
| `references/stages.md:281` | The build ledger exists *"so a compacted context can resume"* — the context problem is acknowledged, never given a rule | partial |
| `pipeline.schema.json` | `stages` + optional `release`; `additionalProperties: true`. No run-wide block | the gap |
| `graphify-out/` | Present. Reach queries add nothing here — the repo is prose, its graph has few edges | built, low value for this task |
| Obsidian wiki `projects/task-pipeline/` | Last synced at v1.6.1; concepts `rules-earned-by-failure`, `one-channel-per-agent` | stale by four releases — stage 9 owes it |

**Therefore not asked:** the branch policy (`main` for doc fixes, branch + PR for
contract changes), the test command, the release path, the doc targets — all
recorded in `CLAUDE.md` and read, not re-litigated.

## Documentation (the phase-1b inventory — the four questions)

`docs/DOCMAP.md` exists and is current. Regime `governed`. Decision home is
`CHANGELOG.md` plus the per-run design record; **no second register is created.**
Gate command `npm test`, guards' own proof `npm run test:all`.

**One divergence found, and it becomes a requirement:** the propagation matrix has
no row for *a change to the config contract* (`pipeline.schema.json`). This run
changes it, so the matrix would be walked with the row missing — the exact shape of
the `root-cause` retro entry from 2026-08-03. Logged as REQ-011.

## Scope

**In:**

- a run-wide **loop mode**, recorded rather than repeated out loud, armed on
  Claude Code with `/loop`;
- a **context-budget rule** that fires on evidence and forbids the guess;
- one new doctrine file carrying both, wired into every surface the propagation
  matrix names;
- the same context rule in the operator's global `~/.claude/CLAUDE.md`, so it
  also governs sessions that are not pipeline runs.

**Out:**

- changing which gates are `manual`. The loop mode does not touch them.
- any new outward capability. `/loop` is armed by the operator or by the recorded
  config; the pipeline never arms it silently.

## Requirements (the REQ spine — every later stage traces to these IDs)

| ID | Requirement | How it's verified | Status |
|---|---|---|---|
| REQ-001 | `pipeline.schema.json` gains a `run` block with `loop` and `contextBudget`; both optional, **absent ⇒ off** | `npm test` — the example is validated against the schema; a planted `run` with a bad enum must be rejected | open |
| REQ-002 | `references/continuity.md` exists and carries both halves | `npm test` — the reach guard (`SKILL.md`), the README-map guard, the portability-manifest guard | open |
| REQ-003 | The loop decision is **surfaced at launch**: preflight block in `SKILL.md`, a row in the grill's autonomy sweep, a row in `templates/brief.md`'s autonomy table | new guard: all three surfaces must name the run mode; negative self-test removes one | open |
| REQ-004 | `build.md`'s unconditional *"Continuous execution"* is reconciled with a default-off recorded mode — no two surfaces disagree | new guard: `build.md` and `stages.md` must cite `continuity.md`, the precedent being the doc-loop reach guard; plus review | open |
| REQ-005 | The context rule states its **evidence condition** and forbids announcing exhaustion without a signal | new guard: the forbidden-guess clause must be present in `continuity.md`; negative self-test deletes it | open |
| REQ-006 | `/loop` is documented with its **real** semantics — fixed short interval, Claude-Code-only, and why a mid-task fire is safe — following `hooks.md`'s harness-limit precedent | review + the guard of REQ-005's family: the harness-limit sentence must be present | open |
| REQ-007 | Every new guard has a negative self-test in `.github/workflows/validate.yml`, and `test/negatives.py`'s floor is raised | `npm run test:all` green, and each new negative watched failing once | open |
| REQ-008 | The propagation matrix is walked: README map, portability manifest, Cursor rule, `CONTRIBUTING.md` invariants, `SKILL-CARD.md`, `CHANGELOG.md`, four-way version sync at **v1.11.0** | `npm test` — four-way version guard, blurb/final-stage guard, invariant-citation guard | open |
| REQ-009 | The context rule also lands in `~/.claude/CLAUDE.md`, **with the diff shown before it is written** | the operator sees the diff; `grep` in the file afterwards. No repo check — stated honestly | open |
| REQ-010 | `pipeline.example.json` ships `run` **explicitly off**, so the example demonstrates the default instead of relying on its absence | `npm test` — example-vs-schema validation, plus a guard that the example carries the block | open |
| REQ-011 | `docs/DOCMAP.md` gains a propagation row for **a change to the config contract** | review — no check can decide whether a matrix row is missing; the absence itself is the evidence | open |
| REQ-012 | Every relative link in a seeded template resolves **from the destination the doctrine seeds it to**, not only from `templates/` | new guard: seed each template to its documented destination in a scratch tree and run the existing link resolver over it; negative self-test plants a `../`-relative link | open (added at stage 1) |

Frozen. Adding is free; removing needs the operator's explicit agreement.
**REQ-012 was added at stage 1**, from a defect the run hit itself — the addition
is recorded here rather than folded silently into REQ-002.

## Users & context

The operator, and every project that installs this skill. The failure being fixed
is concrete: the operator repeats *"run the list in a loop, one task per iteration,
no pause"* every run, and receives *"context is nearly exhausted"* while the window
is largely free.

## Decisions locked (the grill's output)

| # | Decision | Rationale |
|---|---|---|
| D-1 | The loop mode spans the **whole run** — stage-5 plan tasks, `auto` gates, the per-module program loop, the acceptance→retro tail | The operator's answer. A mode that stops at one stage boundary is the failure being fixed |
| D-2 | `manual` gates and outward acts are **never** collapsed by the mode | Repository floor: a generic flag is not a specific authorization |
| D-3 | The threshold fires **only** on a harness signal (compaction warning, `PreCompact`) or the operator saying so | There is no tool that reports context percentage. A number the agent estimates is the guess that caused the complaint |
| D-4 | Home: a `run` block in `pipeline.schema.json` **and** `references/continuity.md` | A project sets it once and is never asked again — which is what "stop repeating it" actually requires |
| D-5 | Canonical Claude Code form: `/loop <interval> <invocation>`, a **fixed short interval** | The operator's answer, against my recommendation of the self-paced form. The mid-task-fire risk is closed by the build ledger: `Task <N>: complete` is the only DONE marker, so a fire inside a task resumes it |
| D-6 | Default **off** when unrecorded | The operator's instruction, and it matches the deploy-authorization floor: silence authorizes nothing |
| D-7 | The context rule also goes into the global `~/.claude/CLAUDE.md` | The complaint was about sessions in general, not only runs |

## Autonomy (the sweep — stages 1→10 read this instead of asking)

| Stage | Answer |
|---|---|
| run-wide | Model: Opus 5, confirmed once. Decide alone inside the repository; escalate the tag push and the global-file write |
| run-wide loop | **On for this run**, armed by the operator with `/loop` if they choose; the pipeline does not arm it itself |
| 0 Harvest | Sources as tabled. Wiki writable at stage 9; the code graph is refreshed in place |
| 0 Docs regime | `governed`; decision home `CHANGELOG.md`; gate `npm test`; this run may not lower a floor and does raise the negatives floor |
| 1 Docs | No external library. The one external contract is the harness's `/loop`, grounded from the tool contract, never from recall |
| 2 Decompose | One module. Not a platform |
| 2–3 Spec | Not user-facing UI. No super-ux track, no scenario tracing |
| 4–5 Dev | Branch `run-continuity`, PR into `main` — this changes a public contract, so `CLAUDE.md` forbids landing it straight on `main`. Conventional commits with the version suffix |
| 5 Integration | Inline run, no subagents (the operator's standing instruction for this session). Self-review declared as weaker evidence |
| 6 Tests | `npm run test:all`. Green means `PASS: task-pipeline structure valid` plus every negative rejecting. Corrupt files in **python, never `sed -i`** |
| 7 Lint+deploy | The validator is the lint. Tag `v1.11.0` — **outward, needs an explicit go** |
| 8 Post-deploy | The release workflow's `npx` smoke test, then `npm view task-pipeline-skill version`, then `npx --yes sshlg-skills@latest update` per the global ops rule |
| 9 Docs+wiki | README, CHANGELOG, SKILL-CARD, DOCMAP, Cursor rule, portability manifest; `wiki-update`; `/graphify . --update` |
| 10 Acceptance | The operator signs off. Deferred rows go to the carry-over ledger. Retro exists; R-001 and R-002 bind this run |

## Done-criteria

Every REQ row verified with evidence from a check seen failing once; the suite and
its negatives green; the release tagged and smoke-tested; docs, wiki and graph
closed; the retro pruned, stamped and written.

## Open assumptions / risks

- ~~**`/loop`'s minimum interval is not documented to me.**~~ **Resolved at stage
  1** — see below. The mechanism was executed, not recalled.
- **REQ-009 leaves the repository.** No guard here can prove a line exists in the
  operator's private global file; the brief says so rather than implying coverage.
- **R-002 binds this run**: any batch of edits that returns an error gets every
  edit in the batch re-verified, not only the one that failed.

## Stage 1 — grounded contracts

No external library is in play. The **one** external contract this change
documents is the harness's own loop mechanism, and this repository's most
expensive past failure was a command described in thirteen files that did
something else when run. So it was **armed and observed in this session**, and
only the observed behaviour is written into doctrine.

| Fact | Evidence |
|---|---|
| `/loop <N>m <prompt>` parses a leading `^\d+[smhd]$` token as the interval; the remainder is the prompt | the loop skill's own parsing rules, applied to this run's input |
| `Nm` for N ≤ 59 becomes the cron expression `*/N * * * *`, scheduled with `recurring: true` | this run: `5m` → `*/5 * * * *`, job `1c656ab5` |
| The job is **session-only** — never written to disk, gone when the session ends | the scheduler's own return value |
| Recurring jobs **auto-expire after 7 days**, firing one final time | same |
| **Jobs fire only while the REPL is idle — never mid-query** | the scheduler's documented runtime behaviour |
| Recurring fires carry jitter: up to 10% of the period late, capped at 15 minutes | same |
| An interval that does not divide its unit cleanly (`7m`, `90m`) must be rounded to one that does, and the rounding said out loud | the loop skill's interval table |
| With **no** interval, the loop self-paces instead, and the delay is clamped to 60–3600 s | the wakeup tool's contract |
| Loops of ≥60 minutes or daily cadence belong in the cloud scheduler, not here | the loop skill's cloud-offer rule |

**This retires the risk recorded against D-5, and it retires it by construction
rather than by care.** The objection to a fixed interval was that a fire could
land inside an unfinished task and cause the completed work to be re-run. It
cannot: the scheduler only enqueues while the REPL is idle. The build ledger
remains the second line of defence for a fire that lands between two tasks after
a context loss — but the first line is that the interrupt this risk assumed does
not exist. **Doctrine must say both, and must not claim the ledger is what makes
the interval safe.**

Two consequences for what gets written:

1. The doctrine names an interval **form**, never a magic number, and states the
   rounding rule and the 7-day expiry, because a loop that silently dies on day
   eight is worse than one that was never armed.
2. `/loop` is **Claude-Code-only**, exactly like the hook contract in
   [`hooks.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/hooks.md).
   The doctrine states the limit out loud and gives the degradation: on a harness
   with no loop primitive, the mode is prose discipline plus the ledger, and the
   run says so rather than pretending it is armed.
