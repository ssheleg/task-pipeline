# Spec — stage 3, built in

Writing the approved design down so a zero-context implementer — human or subagent
— can build from it without asking. Built into this skill; nothing to install.

> The spec write-up, its self-review pass and the operator-review gate are ported
> from the tail of the `brainstorming` skill in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), extended here with the UX track and the Global Constraints block
> that stages 4–5 depend on.

## Contents

- Order of operations
- UX track (user-facing tasks only)
- Write the spec
- Module dossier — when the run is one brick of a platform
- Self-review — before showing it
- Locked contracts are decisions — the register, not only the spec
- GATE (manual)

## Order of operations

For a **user-facing task** (stage-2 UI verdict = yes) the UX chain runs **first** —
scenarios before interface, always. For everything else, go straight to *Write the
spec*.

## UX track (user-facing tasks only)

Runs on **super-ux** — the one companion this pipeline recommends by name
([`companion-skills.md`](companion-skills.md)). If it isn't installed on a UI task,
give the install line and stop; don't improvise a half-chain.

0. **The design destination is already decided — read it, don't re-open it.** When
   Figma is on, the stage-0 brief names the team/org and the file
   ([`grill.md`](grill.md) → *The design destination*), and
   `docs/ux/foundation.md` → *Design tooling* is the canonical record. Confirm the
   recorded file **resolves** before any drawing. **Never create a file when a
   recorded one resolves; if it doesn't resolve, stop and ask — never create a
   replacement.** A creation happens at most once per project, in the team the
   brief names, and its URL goes into the canonical record before the first frame.
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

**Every section carries `covers: REQ-…`** — the brief's requirement ids it serves.
This is what makes the brief→spec seam checkable instead of a re-telling: at the
gate, every REQ must appear in at least one section, and a section that covers no
REQ is either scope creep or a missing REQ. Say which.

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

## Module dossier — when the run is one brick of a platform

If stage 2 produced a module map ([`decomposition.md`](decomposition.md)), this
spec is that module's **dossier**, and it is the only document the module's build
gets. Cover all of it, in this order, each section carrying its `covers: REQ-…`:

1. **Purpose and boundary** — what this module delivers, and what it explicitly
   does not (naming the module that does).
2. **Architecture** — the module's internal shape: units, responsibilities, the
   flow of a request or event through it, and where it sits in the platform.
3. **Entities and data** — the entities this module **owns** (it is their source of
   truth), their fields and invariants, their lifecycle/state transitions, storage
   and migrations. Entities owned elsewhere are referenced by id, never copied into
   a second source of truth.
4. **Contracts — in and out.** For every inbound API/event this module serves and
   every outbound one it consumes: exact signature or schema, auth, idempotency,
   versioning, and **the behavior when the other side is unavailable or wrong**.
   These are the seams the map named; here they get their shapes.
5. **Business logic and rules** — the rules in the domain's language, each with the
   condition that triggers it and the outcome. Rules that only exist as code are
   rules nobody can review.
6. **Edge and failure cases** — the boundaries (empty, first, last, maximum,
   concurrent), the failure modes (timeout, partial write, duplicate delivery,
   downstream down) and the honest degradation for each. This is the section that
   decides whether the module survives contact with production, so it is not a
   bullet list of "handle errors".
7. **UI / Figma** — for a module with a surface: the super-ux chain (foundation →
   flows → screens → scenarios), the `SCR-` screens and their Figma frame links,
   and the states each screen has (loading, empty, error, partial).
8. **Non-functional** — limits, expected volumes, latency budget, security and
   privacy constraints that bind this module specifically.
9. **Open questions** — anything still undecided, with the latest moment it can be
   decided and who decides. An open question that reaches the plan becomes an
   implementer's guess.

A dossier that skips a section says why in one line (`no UI surface`, `owns no
entities`). Silence is not a skip.

Anything the stage-1 docs study could not ground (a library context7 can't resolve,
a private API) is **flagged in the spec** as an assumption, not silently assumed.

## Self-review — before showing it

Read what you wrote with fresh eyes and fix inline. No subagent, no second pass:

1. **REQ coverage:** does every REQ in the brief appear in at least one section's
   `covers:` line, and does every section cover at least one REQ? A missing REQ is
   scope lost here; a section covering none is scope creep or a missing REQ.
2. **Placeholders:** any TBD / TODO / "handle edge cases" / unfinished section? Fix.
3. **Internal consistency:** do sections contradict each other? Does the
   architecture match the feature descriptions and the locked signatures?
4. **Scope:** is this one implementable plan, or does it need decomposition?
5. **Ambiguity:** can any requirement be read two ways? Pick one and say it.
6. **Traceability (UI):** does every user-facing requirement name its scenario ID?
7. **Every check this spec names resolves.** Walk the verification claims — the
   table, and every sentence that says how something is proven. For each: does that
   check exist today, or is this plan building it? A check that is neither is **not**
   a verification: mark it `review` and say so, or build it. This repository's whole
   doctrine is that a green from a check nobody watched fail is not evidence — and
   this stage is where checks are first *named*, which is one step earlier than
   anyone was looking.
8. **Read the decisions back.** Open the brief's `## Decisions locked` table **and**
   the register entries stage 2 recorded for the alternatives it *rejected*
   (`references/brainstorm.md` → *The approved design is a set of decisions*). Does
   any contract here contradict one? Resolve it **out loud** — amend the spec, or
   reverse the decision and record the reversal. A spec that quietly contradicts a
   settled decision re-opens a question the operator already answered.
9. **Print the cost.** Count the surfaces this spec touches, the guards it adds and
   the REQ rows, now versus at stage 2. **Print all three and decide nothing.**
   Growth is information for the operator, whose gate this is; an agent that narrows
   the task on its own judgement breaks *never narrow the task silently*.
10. **Run the hygiene gate** over what this stage wrote and record its counts below.

### The `## Self-review` section — committed, not asserted

The checklist above leaves a **committed trace**, last section before the gate.
Every line carries a **computed number, not a tick**: a number nobody computed is
visible as such, and a checkbox never is. `planning.md` uses the identical shape, so
one habit covers both stages.

```markdown
## Self-review

- REQ coverage: <n> in brief, <n> covered, difference <set or ∅>
- Named checks: <n> named, <n> resolve, <n> marked `review`
- Decisions: checked against <the brief's D-table> and <stage 2's rejected options> — <verdict>
- Cost: <surfaces>/<guards>/<REQ> now, <…> at stage 2 — <proportionate | grown, and why>
- Hygiene: <n> checks, <n> findings, <n> open
- Placeholders: <n> · Ambiguity: <n> found, <n> resolved inline
```

## Locked contracts are decisions — the register, not only the spec

This stage settles more than any other: a schema, a signature, a status vocabulary,
an error shape. Each has a life longer than the document it is written into, so run
the **Doc Loop** ([`documentation.md`](documentation.md)) for the ones that bind
future work — record the entry, propagate by the matrix, and cite the id from the
spec section instead of restating the reasoning there.

**A spec states a contract; the register makes it addressable.** A spec is per-run
and the next one supersedes it; an id survives. If this stage settled something and
no entry names it, the run has agreed to decide it again later.

## GATE (manual)

> "Spec written and committed to `<path>`. Review it and tell me if anything should
> change before I write the implementation plan."

Wait for the operator. Changes requested → apply, re-run the self-review, ask
again.

The gate is not only the operator's word: **every section carries `covers: REQ-…`
and every REQ in the brief appears in at least one section.** For UI tasks it
additionally requires: the chain (foundation → flows → screens → scenarios)
designed, validated and approved; `/ux-lint` green; every user-facing requirement
traced to a scenario ID — or an explicit waiver from the operator recorded in the
spec.

With Figma on, one more, and it is mechanical: **the canonical record names a file,
and every frame link in `screens.md` carries that same file key.** Deep links are
`figma.com/design/:fileKey/…`, so this is a string comparison, not a judgement — a
link whose key differs points at a *second* file, which means the run drew
somewhere nobody will look. Same check at the audit's `F` rung
([`audit.md`](audit.md)); if it ever fires twice, it belongs in the host's lint.

No plan starts before this gate passes.
