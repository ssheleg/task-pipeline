# Task brief — <topic>

> Stage-0 intake artifact. The grill fills this in and the operator confirms it
> before stage 1. Copy to `docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md`.
> Every field is a resolved decision or an explicit deferral — no open unknowns.

- **Date:** YYYY-MM-DD
- **Task (one line):** <what the operator asked for, restated>
- **UI verdict:** yes / no — does this touch a user-facing surface (web/mobile/CLI/TUI)?
  If yes, the stage-3 super-ux UX track is armed.

## Contents

- Knowledge sources (the phase-1 harvest — written BEFORE the first question)
- Documentation (the phase-1b inventory — the four questions)
- Scope
- Requirements (the REQ spine — every later stage traces to these IDs)
- Users & context
- Decisions locked (the grill's output)
- Autonomy (the sweep — stages 1→10 read this instead of asking)
- Done-criteria
- Open assumptions / risks

## Knowledge sources (the phase-1 harvest — written BEFORE the first question)

What the project already knew about this task, and where it said so. One row per
source actually consulted; `none found` is a valid, useful row. Stage 9 updates
this same list — a source worth reading at the start is the next run's false
premise if the run leaves it wrong.

| Source | What it says about this task | Fresh? | Authority | Stale after this run? |
|---|---|---|---|---|
| `docs/adr/NNNN-….md` | … | YYYY-MM | decision | no |
| `graphify-out/graph.json` | reach: what calls it, what breaks if it moves | built YYYY-MM-DD | index | **yes — refresh at stage 9** |
| wiki: `projects/…/concepts/…` | … | YYYY-MM | context | **yes — update at stage 9** |
| `CLAUDE.md` | test/lint/deploy commands, house rules | current | convention | no |

Precedence splits by the question being asked. **For what *is*:** code first, then
host docs and ADRs, then the code graph, then the wiki, then memory — the graph
points, the code decides. **For what *should be*:** the decision register outranks
the code, because a decision accepted and not yet built is still the decision, and
code that contradicts it is a finding rather than a tie-break. The operator
outranks every document — but only **out loud**: an override quoted against its
source is a recorded decision, an unquoted one is an undetected divergence.

## Documentation (the phase-1b inventory — the four questions)

| Question | Answer |
|---|---|
| **Regime** | governed — seeded this run / already in place since … |
| **Decision home** (exactly one) | `docs/DECISIONS.md` (`DEC-####`) / `docs/adr/` (`ADR-NNNN`) — never both |
| **Open questions** | `docs/OPEN_QUESTIONS.md` (`OQ-####`) |
| **Doc map** | `docs/DOCMAP.md` — single homes + the propagation matrix (non-empty; every row names its check or the word `review` with a reason) |
| **Gate** | `bash scripts/check-docs.sh` — seeded / already present; ratchet floors: … |
| **Shared state** | lease mechanism present / **`ungated`** (say so out loud in the run) |
| **Intent vs as-built** | reconciled on … ; divergences found: … ; each resolved how |

- **Doc repos / hosted doc systems this project names:** … (or `none`)
- **Knowledge wiki:** installed / not installed
  ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki); recommended, never a gate)
- **Retro, in force:** `docs/superpowers/retro.md` — none / N standing instructions
  (read **in full**, together with the run stamps and the recent-log window; list
  which ones bind this run, and stamp each as it fires **with the commit** — that
  stamp is the only evidence behind stage 10's cold-retirement rule)
- **Retro archive:** `docs/superpowers/retro/` — **queried** by this task's nouns;
  what it returned: … (or `nothing`)
- **Code graph:** built / installed-not-built / not installed
  ([graphify](https://github.com/Graphify-Labs/graphify); recommended, never a gate —
  built → its row above carries the build date and stage 9 refreshes it)

## Scope

- **In scope:** …
- **Out of scope / explicitly deferred:** … (with the reason and, for deferrals,
  the latest moment the decision can still be made)

## Requirements (the REQ spine — every later stage traces to these IDs)

Scope above is prose; this is the **addressable** form of it. One row per
independently verifiable deliverable — not one per sentence. Every row needs a
named check: **a requirement you can't say how to verify is a badly-stated
requirement** — split it here, on the grill, not at acceptance.

| ID | Requirement | How it's verified | Status |
|---|---|---|---|
| REQ-001 | … | test name / `file:line` / command + expected output / `SCN-…` | open |
| REQ-002 | … | … | open |

Status lifecycle, written at three checkpoints only (stage 4, stage 5, stage 10 —
not continuously): `open` → `planned` → `built` → `verified` \| `partial` \|
`deferred` \| `dropped`.

> **The list is frozen once confirmed.** Adding a requirement mid-run is fine —
> append it with its source. **Removing or narrowing one needs the operator's
> explicit agreement**, recorded in the carry-over ledger. Silently restating the
> task in smaller terms is the failure this table exists to prevent: every gate
> after it goes green on the shrunken task and nothing reports the loss.

## Users & context

- **Who / for what:** … (personas, the job being done)
- **Where it runs / constraints:** platform, runtime, data, integrations, limits

## Decisions locked (the grill's output)

| # | Decision | Chosen | Rationale |
|---|---|---|---|
| 1 | … | … | … |

## Autonomy (the sweep — stages 1→10 read this instead of asking)

Every row is either a resolved answer or an explicit **STOP AND ASK**. A blank row
is not neutral — it is a scheduled interruption.

| Stage | Question | Answer |
|---|---|---|
| run-wide | Model for this run | … (most capable available unless overridden; per-stage overrides here) |
| run-wide Escalation | … | cost of being wrong: decide alone while it stays inside the repository and reversible; escalate price, legal posture, promise, money, reputation, irreversible outward acts. Project exceptions? |
| run-wide | Decide autonomously vs escalate to me | … |
| run-wide Pacing | Run mode: item-by-item with no check-in between items, and on what interval? (the skill's `references/continuity.md`; read `pipeline.json` → `run.loop` first) | … (**absent ⇒ off**; it never collapses a manual gate or an outward act) |
| 0 Harvest | Doc sources beyond this repo — other repos, hosted docs, the knowledge wiki, the code graph; and may stage 9 write to them? | … (another repo is outward: propose + PR, never a direct push; graph built / not built) |
| 0 Setup audit | … (yes / no — recorded either way) | doc map absent or stale: run the entry audit over the existing documentation before building on it (the skill's `references/setup.md`)? Asked once; a refusal is recorded and never re-asked |
| 0 Docs regime | Where settled things live (register or ADR set — one home, never both); who may write it; lease mechanism present, or is this run `ungated`? Gate command + ratchet floors; may this run raise a floor? | … |
| 1 Docs | External libs/APIs/SDKs in play; any context7 can't resolve → where their docs live | … |
| 2 Decompose | Platform (several capabilities/surfaces) or one module? If platform — deploy cadence: per module, or once at the end | … |
| 2–3 Spec | UI verdict (arms super-ux); scenario-tracing waiver, if any | … |
| 3 Design surface | UI only: Figma on or text-only (check `docs/ux/foundation.md` → Design tooling first); Figma MCP connected? **If not — ship text-only, or stop and connect it?** | … (super-ux never blocks on a missing MCP, so an unanswered row here ships the feature without mockups) |
| 3 Design file | Figma on only: **which team/org + which file** — existing URL, or "create one in team `<name>`" **with creation authorized**. Canonical record: `docs/ux/foundation.md` → Design tooling | … (team: `<name>` · file: `<url>` \| `create in <team>, authorized` — never create when a recorded file resolves) |
| 4–5 Dev | Base branch; worktree/branch policy; is `main` off-limits; commit convention; task tracker | … |
| 5 Integration | How the branch lands — direct merge, PR (who approves), or "leave it, I'll merge"; is parallel fan-out (one worktree per implementer) wanted? | … |
| 6 Tests | Test command; what "green" means; known-red baseline; coverage expectation | … |
| 7 Lint | Lint command (incl. `docs/ux/lint.py` for UI projects) | … |
| 7 Deploy | Target + path; release automation on/off; deploy-from-main rule | … |
| 7 Deploy | **Authorization** — standing go, or ask every time? | … |
| 8 Post-deploy | Where logs / health live (app name, endpoint, workflow) | … |
| 9 Docs+wiki | Which module docs / runbooks this change updates; wiki sync yes/no; **code-graph refresh yes/no** (`/graphify . --update`); which stale ledger rows get fixed | … |
| 10 Acceptance | Who signs off; where deferred REQs get tracked (issue tracker / backlog); **retro file** — `docs/superpowers/retro.md` present? which standing instructions bind this run? | … |

> **Deploy authorization has a hard floor.** A standing go counts only if it is
> **specific** — named target and named preconditions ("staging, once lint and the
> full suite are green; production always asks"). Vague blanket permission does not
> authorize an outward, irreversible action; stage 7 stops and asks.

## Done-criteria

- Observable, verifiable conditions that mean "this task is finished".

## Open assumptions / risks

- Assumption → how it's validated (or flagged risky-untested).
