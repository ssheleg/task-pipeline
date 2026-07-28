# Task brief — <topic>

> Stage-0 intake artifact. The grill fills this in and the operator confirms it
> before stage 1. Copy to `docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md`.
> Every field is a resolved decision or an explicit deferral — no open unknowns.

- **Date:** YYYY-MM-DD
- **Task (one line):** <what the operator asked for, restated>
- **UI verdict:** yes / no — does this touch a user-facing surface (web/mobile/CLI/TUI)?
  If yes, the stage-3 super-ux UX track is armed.

## Scope

- **In scope:** …
- **Out of scope / explicitly deferred:** … (with the reason and, for deferrals,
  the latest moment the decision can still be made)

## Users & context

- **Who / for what:** … (personas, the job being done)
- **Where it runs / constraints:** platform, runtime, data, integrations, limits

## Decisions locked (the grill's output)

| # | Decision | Chosen | Rationale |
|---|---|---|---|
| 1 | … | … | … |

## Autonomy (the sweep — stages 1→9 read this instead of asking)

Every row is either a resolved answer or an explicit **STOP AND ASK**. A blank row
is not neutral — it is a scheduled interruption.

| Stage | Question | Answer |
|---|---|---|
| run-wide | Model for this run | … (most capable available unless overridden; per-stage overrides here) |
| run-wide | Decide autonomously vs escalate to me | … |
| 1 Docs | External libs/APIs/SDKs in play; any context7 can't resolve → where their docs live | … |
| 2–3 Spec | UI verdict (arms super-ux); scenario-tracing waiver, if any | … |
| 4–5 Dev | Base branch; worktree/branch policy; is `main` off-limits; commit convention; task tracker | … |
| 5 Integration | How the branch lands — direct merge, PR (who approves), or "leave it, I'll merge"; is parallel fan-out (one worktree per implementer) wanted? | … |
| 6 Tests | Test command; what "green" means; known-red baseline; coverage expectation | … |
| 7 Lint | Lint command (incl. `docs/ux/lint.py` for UI projects) | … |
| 7 Deploy | Target + path; release automation on/off; deploy-from-main rule | … |
| 7 Deploy | **Authorization** — standing go, or ask every time? | … |
| 8 Post-deploy | Where logs / health live (app name, endpoint, workflow) | … |
| 9 Docs+wiki | Which module docs / runbooks this change updates; wiki sync yes/no | … |

> **Deploy authorization has a hard floor.** A standing go counts only if it is
> **specific** — named target and named preconditions ("staging, once lint and the
> full suite are green; production always asks"). Vague blanket permission does not
> authorize an outward, irreversible action; stage 7 stops and asks.

## Done-criteria

- Observable, verifiable conditions that mean "this task is finished".

## Open assumptions / risks

- Assumption → how it's validated (or flagged risky-untested).
