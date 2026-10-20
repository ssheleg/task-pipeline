# Stage 0 detail

The full gate and freedom level remain in [stages.md](stages.md).

## Contents

- 0 — Intake grill — MANDATORY

## 0 — Intake grill — MANDATORY
- **Stage 0 always runs, and its depth is proportional.** The gap check, the
  harvest and the brief are never skipped; the interview, the committed brief file
  and stages 1-4 are what a small change does without (Phase 1d below, the
  *proportional run*). A run that starts building without a brief and its REQ rows
  (in the brief file, or on the short path in the run ledger) is a **failed run**:
  stop and go back. The entry-from-super-ux short-circuit below is the other
  sanctioned shortening.
- **Entry-from-super-ux short-circuit (check FIRST).** task-pipeline is often
  launched *from* super-ux — its `/ux` action menu offers "execute autonomously
  via the task-pipeline plugin" once the UX chain (and often a
  `docs/ux/plans/…` fix plan) is already built. Before grilling, detect that:
  if `docs/ux/` already holds a validated chain (foundation → flows → screens →
  scenarios) and/or a fresh fix plan, **do not re-run the grill or the stage-3
  UX track from scratch.** Instead: (1) run a quick check — `/ux-lint`
  (`docs/ux/lint.py`) green, chain present, plan (if any) readable; (2) confirm
  the scope with the operator in ONE line; (3) skip to the first stage that
  still has real work (usually stage 4 Plan if a UX fix plan already exists, or
  stage 3 Spec to formalize it). Record what was adopted vs skipped. If the
  check finds drift/gaps, fall back to the normal flow for the missing parts
  only.
- **What (normal entry):** the operator's one-line task is almost never enough to
  run autonomously. Before anything else, **grill the operator** to expand that
  one line into a complete, unambiguous brief — resolve every decision branch
  up front so stages 1→10 need no further human input beyond the manual gates.
  This is input expansion, not design: turn "make me feature X" into locked
  answers for scope, users, constraints, data, edge cases, done-criteria.
- **Phase 1 — harvest the knowledge sources FIRST**
  ([`knowledge-sources.md`](knowledge-sources.md)). Before the first question:
  query what the project already knows about this task — code, **the code graph**
  when one is built ([`knowledge-graph.md`](knowledge-graph.md): `graphify query` /
  `affected` / `god-nodes` answer *reach*, which is what grep cannot), `CLAUDE.md`,
  `CONTEXT.md`/ADRs, `docs/` + `docs/ux/`, past pipeline briefs and carry-over
  ledgers, **the retro's standing instructions and run stamps** (`<artifacts>/retro.md`,
  read **in full**: ten standing rows and ten stamps, bounded by a cap and by a byte
  budget; print `scripts/retro_budget.py check` first, which states the floor's bytes and
  bytes/4 tokens. They bind this run; stamp each instruction as it fires. Its *Recent log* is **queried** by the
  task's nouns, not read: uncapped narrative inside a binding source is what makes the
  capped part get skimmed, [`retrospective.md`](retrospective.md)), **lessons from other
  projects** (source 7b, [`knowledge-sources.md`](knowledge-sources.md): `scripts/lessons.py
  query` over the local index, then a shared store where the session lists one — each
  layer's state printed in the source ledger), the **knowledge wiki** if one is
  installed
  ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki) — recommended,
  never required), and any **other repo or hosted doc system the project names as
  its docs**. Write the **source ledger** into the brief (a row per source, or an
  explicit "none found"; **the graph's row carries its measured lag — commits and
  days behind `HEAD`, the signal that measured it, and `⚠ not trusted for reach
  until refreshed` on anything but `current`**
  ([`knowledge-graph.md`](knowledge-graph.md) → *Measure the lag*; a build date is
  the graph's own reply about itself, not a measurement of it). It is retrieval
  scoped by the task's own nouns, not a read of everything — and it is what makes
  phase 2's answers checkable instead of merely confident.
- **Phase 1b — the documentation inventory**
  ([`documentation.md`](documentation.md)). Four questions, answered before the
  interview and written to `docs/DOCMAP.md` (seeded from
  [`../templates/docmap.md`](../templates/docmap.md), **only when absent**): where
  do settled things live, what is each fact's single home, what does a change of
  type X oblige, and what proves it. A project with no answers gets them seeded —
  registers, the matrix and `scripts/check-docs.sh` — and the seeding is itself
  recorded as the register's first entry. **One decision home per project:** an
  existing `docs/adr/` *is* the register and is recorded as such, never duplicated.
  The gate is seeded so that it exits `0` on its own seeds; a project that starts
  red learns on day one that the gate is noise.
- **Phase 1b+ — offer the entry audit, once** ([`setup.md`](setup.md)). When
  `docs/DOCMAP.md` is absent or its regime line predates the project's last release,
  ask whether to audit the documentation that already exists **before** building on
  it. Record the answer — including a refusal — in the brief's autonomy sweep and
  never ask again. `audit.md`'s ladder runs at the *end* over the change; this runs
  at the *start* over what is already there.
- **Phase 1c — reconcile intent against as-built.** Git says how it *should* be;
  the run record says how it *turned out*. Read both for the area you are about to
  touch and resolve every divergence — the document is stale, the record is wrong,
  or they genuinely disagree and that is a decision. There is no fourth option, and
  starting on an unresolved divergence means building against a system that does
  not exist.
- **Phase 1d — the short-path triage, and the proportional run: a small change
  takes the short path by default.** This pipeline's boundary exempts a typo and a one-line edit; until 1.98.0
  the next size up still met eleven stages and five manual gates, because the short
  path was only *proposed* and silence took the full flow. Under a standing "decide and
  act" instruction silence is the normal answer, so a proposal was the full flow every
  time. The triage now **decides**, from five answers with something behind each:

  ```
  1. files the change touches, resolved      git ls-files -- <paths>       -> N
  2. any of them a public contract            the surfaces the host's release
                                              syncs, its schema or config
                                              contracts, a shipped command,
                                              its README                    -> yes/no
  3. behaviour a user observes changes        a UI, a message, an output    -> yes/no
  4. a deploy target in the brief             stage 7's target exists       -> yes/no
  5. risk class                               work-graph.md R1-R3           -> R1/R2/R3
  ```

  **Small** means all of: the gap check left zero material unknowns, N ≤ 5, no public
  contract, no user-observable change, no deploy, and risk **R1**. Small ⇒ the run takes
  the short path and prints one line:
  `short path: R1 · N files · no contract · no user-facing change · no deploy`.
  `scripts/short_path.py` computes the decision from the five answers (exit 0 short,
  3 full) and prints that line.
  The short path is: the brief and its REQ rows written into the run ledger (no grill,
  no committed brief file) → stage 5, build with tests → stage 6, the suite plus **one**
  verification (one blind tier, [`certification.md`](certification.md)) → stage 9, the
  docs the change makes false and the handoff → stage 10, the hand-back and a run stamp;
  a retro entry only when the run taught a new lesson. Stages 1-4, 7 and 8 print `⊘`
  with the triage line as their reason ([`progress.md`](progress.md)).
  **Triggers that bring a skipped stage back:** a deploy target appears (7, 8); a wiki or
  code graph exists and the change touched what it indexes (9 in full); a check reveals a
  contract or a user-facing effect (leave the short path, resume at stage 2); the
  operator asks for the full cycle. Any answer outside *small* takes the full flow,
  printed the same way with the failing answer as its reason.
- **How it runs: [`grill.md`](grill.md)**, read only when the gap check leaves a
  material unknown (a complete brief asks nothing). In short: close what the sources can, then ONE batch
  of the material unknowns, ordered by dependency, a recommended answer with each —
  one at a time only where answers depend on each other or the operator asks;
  contradictions reconciled on the spot; **every answer that touches
  a harvested source is checked against it** — the operator outranks any document,
  but only out loud, and the losing side is logged for the stage-9 doc update; plus
  **domain awareness**
  (challenge terms against `CONTEXT.md`, sharpen fuzzy language, stress-test with
  concrete scenarios, cross-reference the code, record ADRs for hard-to-reverse
  calls) and the **autonomy sweep** that pre-resolves every stage-1→10 blocker.
  Deploy authorization has a hard floor there: a standing go counts only when it
  names the target and the preconditions.
- **The run mode is settled here too** ([`continuity.md`](continuity.md)): does
  the run advance item-by-item with no check-in between items, and on what
  interval? Exactly three sources arm it: `pipeline.json` → `run.loop` (read
  first — a recorded mode is the answer and is not re-asked), the operator's answer
  here, or a standing instruction the host already carries. The ledger names which, once:
  `loop: armed by <source:line>`. **Absent all three, it is off.** It buys pacing, never
  authorization: no loop mode collapses a `manual` gate or an outward act. The
  same file carries the other half of pacing — the context budget, which fires
  only on a harness signal or the operator's word, never on an estimate.
- **UI early-detect:** one branch of the grill is always "does this touch a
  user-facing surface (web/mobile/CLI/TUI)?". If yes → surface **super-ux**
  now (use it if installed; otherwise give the install line — see SKILL.md
  *Prerequisites*); this arms the stage-3 UX track. **And the same branch records
  the surface's class** — the next bullet.
- **The surface class.** Every user-facing task's brief carries
  `surface_class: flagship | product | internal | ad`, and the class selects the gate
  profile the visual layer is held to for the rest of the run:

  | Class | What it is | Director record (stage 3) | Visual half (stages 5–6) | Stage 10 |
  |---|---|---|---|---|
  | `flagship` | the surface a product is judged by — landing, onboarding, paywall, a hero screen | the full record | **gate**: full matrix, pairwise across every axis, the full rubric | approved contact sheet |
  | `product` | an ordinary screen of the product | the short record — Brief, Mode, References, Markers, Open | **gate**: every state and the mandatory pairs; the gate items of the rubric | approved contact sheet |
  | `internal` | an admin panel, an internal tool, a CLI | none owed | recommended; the project linter is the floor | the functional look |
  | `ad` | a creative that runs as an advertisement or a store asset | Brief, Mode, References, Markers, ADA (its rubric profile and safe zones), Open | **gate**: the ad profile and the safe zones | approved contact sheet |

  Ask it as one question with a recommended answer read off the request — a landing or a
  paywall is `flagship` unless the operator says otherwise — and never leave it to stage
  5: a class decided at build time is decided by whoever wants the build to pass. A
  work-graph node that builds the surface copies the class as `surface_class`, and
  `graph.py certify` then owes the fourth, `visual` reading on `flagship` and `product`
  ([`certification.md`](certification.md) → *The fourth reading*).
- **Artifact:** lock the resolved decisions into a **task brief** committed at
  `<artifacts>/specs/YYYY-MM-DD-<topic>-brief.md` (scope, users/UI verdict and,
  for a user-facing task, `surface_class`, constraints, assumptions, explicitly-deferred items, done-criteria) **plus the
  autonomy sweep's per-stage answers and the model decision**. Seed it from
  the skill's `templates/brief.md` skeleton — but only when absent, never
  overwrite an existing brief. Stages 2–4 build on this brief; stages 5–10 read
  its autonomy section instead of asking. Where the session produced them, also:
  an updated `CONTEXT.md` (terms written as they resolved) and any ADRs under
  `docs/adr/` — see `grill.md` → *Domain awareness*.
