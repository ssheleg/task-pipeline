# Spec — stage 3, built in

Writing the approved design down so a zero-context implementer — human or subagent
— can build from it without asking. Built into this skill; nothing to install.

> The spec write-up, its self-review pass and the operator-review gate are ported
> from the tail of the `brainstorming` skill in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), extended here with the UX track and the Global Constraints block
> that stages 4–5 depend on.

## Order of operations

For a **user-facing task** (stage-2 UI verdict = yes) the UX chain runs **first** —
scenarios before interface, always. For everything else, go straight to *Write the
spec*.

## UX track (user-facing tasks only)

Runs on **super-ux** — the one companion this pipeline recommends by name
([`companion-skills.md`](companion-skills.md)). If it isn't installed on a UI task,
give the install line and stop; don't improvise a half-chain.

1. `/ux` — the single super-ux entry: reports which `docs/ux/` layers exist,
   repairs the skeleton, records the Figma on/off choice, recommends the next
   action. Never make the operator pick skills.
2. `ux-foundation` → `docs/ux/foundation.md` — the **WHY**: personas, Jobs to Be
   Done, customer journey maps, user stories (Given/When/Then).
3. `ux-flows` → `docs/ux/flows.md` + `docs/ux/screens.md` — the **HOW + UI map**:
   task analysis, user-flow diagrams (branches, error paths), every screen and
   state with a wireframe and, when Figma is on, a frame link.
4. `ux-scenarios` → `docs/ux/scenarios.md` — the **WHAT**, the source of truth for
   user-facing behavior: scenarios validated against super-ux's format contract —
   IDs, statuses, `Traces:` to stories / journey stages / flows, edge and error
   states enumerated.
5. **Run the linter** (`/ux-lint`, i.e. `python3 docs/ux/lint.py`). It must pass:
   no drift, no orphans, no broken traces, no stale Figma links.

These skills are **idempotent** — extend the existing `docs/ux/` layers, never
rebuild them. If the chain already exists and is validated (typically when the run
entered from super-ux), verify it and embed it; build only what's missing.

## Write the spec

Path: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, committed, **same
`<topic>` slug as the brief** so brief → design → plan is traceable at a glance.
(The directory name is this pipeline's historical convention, not a dependency on
anything; a host project may relocate the root via its `CLAUDE.md` — keep the
shape. See [`artifacts.md`](artifacts.md).)

The spec **locks every shared contract**, because from here on people and subagents
work from it in parallel and can't renegotiate:

- **Types, schemas, signatures** — exact names, exact parameter and return types.
- **File layout** — which files exist, what each one owns.
- **Global Constraints** — the project-wide requirements every task inherits:
  version floors, dependency limits, naming and copy rules, platform requirements,
  exact values. Stage 4 copies this block verbatim into the plan and stage 5 hands
  it to every reviewer, so write it as literal values, never as prose.
- **Error handling and degradation** — what fails how, what the user sees, what
  gets logged.
- **Testing approach** — what proves this works.

For UI tasks the spec **embeds the UX layer**: the validated scenario IDs, the
flows and `SCR-` screens, the CJM stages the feature serves, and the applicable
super-ux patterns and principles. Every user-facing requirement traces to a
scenario ID.

Anything the stage-1 docs study could not ground (a library context7 can't resolve,
a private API) is **flagged in the spec** as an assumption, not silently assumed.

## Self-review — before showing it

Read what you wrote with fresh eyes and fix inline. No subagent, no second pass:

1. **Placeholders:** any TBD / TODO / "handle edge cases" / unfinished section? Fix.
2. **Internal consistency:** do sections contradict each other? Does the
   architecture match the feature descriptions and the locked signatures?
3. **Scope:** is this one implementable plan, or does it need decomposition?
4. **Ambiguity:** can any requirement be read two ways? Pick one and say it.
5. **Traceability (UI):** does every user-facing requirement name its scenario ID?

## GATE (manual)

> "Spec written and committed to `<path>`. Review it and tell me if anything should
> change before I write the implementation plan."

Wait for the operator. Changes requested → apply, re-run the self-review, ask
again. For UI tasks the gate additionally requires: the chain (foundation → flows →
screens → scenarios) designed, validated and approved; `/ux-lint` green; every
user-facing requirement traced to a scenario ID — or an explicit waiver from the
operator recorded in the spec.

No plan starts before this gate passes.
