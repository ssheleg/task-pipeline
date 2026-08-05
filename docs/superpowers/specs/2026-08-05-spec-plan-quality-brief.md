# Task brief — spec and plan quality: the read-back

**Run:** `spec-plan-quality` · 2026-08-05 · model: Opus 5 (top tier available,
confirmed at preflight, no per-stage overrides)

Stages 3 and 4 produce documents that state things nobody verifies: that a named
check exists, that the spec agrees with decisions already made, that the self-review
happened at all, and that the change still costs what it was worth. Five defects,
four of them with an incident from the run that preceded this one.

**They are one shape, not five.** In four of the five cases the rule already exists
somewhere in this bundle — and lives in a stage that never hands it to the stage
which would act on it. The fix is therefore one mechanism applied four times: a
**read-back**, where the stage that must obey a rule is told to go and read it.

## Contents

- Knowledge sources
- Documentation
- The five defects
- Scope
- Requirements (the REQ spine)
- Decisions locked
- Autonomy
- Done-criteria
- Open assumptions / risks

## Knowledge sources (the phase-1 harvest — written BEFORE the first question)

| Source | What it says about this task | Fresh? |
|---|---|---|
| `references/spec.md` (read in full) | Strong: `covers: REQ-…` per section, a 6-item self-review, the module dossier, the Doc Loop, a gate with mechanical criteria. **No item asks whether a named check exists; no artifact proves the self-review ran** | current — the gaps are absences, not errors |
| `references/planning.md` (read in full) | Stronger: set-equality is **printed**, dependency graph, exclusive file ownership, and *"this stage settles nothing"* as an explicit rule. **No item asks whether a DoD's command resolves** | current |
| `references/brainstorm.md:105–111` | **"An approved approach is a decision, and so is each alternative rejected for a reason worth remembering… the option deliberately not taken."** Doc Loop required. States the cost precisely: a design recorded only in the spec dies with it and the next run re-opens a settled question | current — **and violated by the previous run**, which is D3's incident |
| `references/learned.md:157` | Rule 14, *"every target resolvable"*, is mapped to **stage 9 only**. Stages 3 and 4 — where a target is first *named* — never see it | current; the reach is the defect |
| `templates/brief.md:104` | The brief already carries **`## Decisions locked`** with `# / Decision / Chosen / Rationale`. So D3's read-back has a real source and needs no new artifact | current |
| `references/grill.md:146` | Cost appears only as *when to escalate*, never as *is this worth doing*. Confirmed absent | current |
| `docs/superpowers/retro.md` | R-001 and R-002 in force. The recurring lesson in the log — *"declaring a thing cross-cutting does not distribute it"* — is this task's diagnosis, already written down twice about other rules | current |
| `docs/DOCMAP.md:44` | Propagation rows that fire: *a new document, rule or guard*; *a new or changed guard*; *a user-visible capability* | current |
| The aborted `superpowers-bridge` run | Four incidents, all in this session's transcript, all reproducible from the deleted branch's reasoning. Branch deleted by the operator; the incidents are cited from the conversation, not from git | evidence, not artefact |

## Documentation (the phase-1b inventory)

`docs/DOCMAP.md` current, regime `governed`. Decision home is `CHANGELOG.md` plus
the per-run design record; no second register. Gate `npm test`; guards' proof
`npm run test:all`.

**Intent vs as-built:** no divergence found. `spec.md` and `planning.md` both
describe accurately what they do — the problem is what they omit, which is why this
run adds and never corrects.

## The five defects

| # | Defect | The rule that already exists, and where it is stranded | Incident |
|---|---|---|---|
| **D1** | The spec names checks; nothing asks whether they exist | `audit.md` / `gates.md`: *a green from a check nobody watched fail is not evidence*. Stranded at stages 6 and 10 | Previous run's spec claimed REQ-008 was verified by a mechanical cross-surface comparison. No such comparison exists |
| **D2** | The self-review leaves no artifact — *"run the checklist yourself, inline"* | `planning.md` already demands the set difference be **printed**. The principle exists one item away from where it is missing | "Self-review passed" was unfalsifiable in the previous run; it happened to be run honestly, which is not a property of the doctrine |
| **D3** | Nothing reconciles the spec against decisions already made | `brainstorm.md:105`: rejected alternatives are decisions and go through the Doc Loop. Stranded at stage 2 — no stage-3 item reads them back | Approach C rejected at stage 2 ("it would break every host config"); a schema change accepted at contract 11 of the same spec. Unnoticed until the operator asked a direct question |
| **D4** | No cost checkpoint. The self-review asks about *size* ("needs decomposition?"), never about *worth* | Nothing — this one is a genuine absence, not a stranding | Scope went from "add a recommendation" to 17 REQs, 12 surfaces, 2 guards and a schema change. No gate ever printed that growth |
| **D5** | A plan's DoD may name a command that does not exist | `learned.md` rule 14, *every target resolvable*, mapped to stage 9 only | None in this session — found by reading. Recorded as such: weaker evidence than the other four, and it is the same class as D1 |

## Scope

**In:**

- four read-backs and one new checkpoint, all inside `references/spec.md` and
  `references/planning.md`;
- a required `## Self-review` section in both stage artifacts, carrying **computed
  numbers, not ticks**;
- `learned.md` rule 14's stage map extended to 3 and 4;
- the stage-3 and stage-4 gate criteria in `references/stages.md` updated to demand
  the section;
- guards proving the doctrine files carry the new items, with negative self-tests;
- the propagation surfaces the matrix names for those change types.

**Out:**

- **any change to `grill.md`.** D4's checkpoint belongs at stage 3, where the surface
  count is finally knowable; at stage 0 nobody can predict twelve surfaces. Adding a
  stage-0 question would ask for a number that does not exist yet;
- **a numeric threshold for D4.** Decided below (D3 in *Decisions locked*): the
  checkpoint prints and the operator decides. A threshold invented here would either
  fire on noise or stay silent;
- rewriting either file. Both are accurate; this run adds;
- the module dossier, the UX track, and every existing self-review item — untouched.

## Requirements (the REQ spine — every later stage traces to these IDs)

Frozen at stage 0. Adding is free; removing needs the operator's explicit word.

| id | Requirement | Verified by |
|---|---|---|
| REQ-001 | `spec.md` self-review gains **"every check this spec names resolves"** — a check that does not exist is either built or marked `review`, never asserted (D1) | guard: the item's literal is present in `spec.md`; probed by deleting it |
| REQ-002 | `spec.md` requires a committed **`## Self-review`** section with computed values — REQ counts and the difference, checks named vs resolving, decisions reconciled, cost delta, placeholder and ambiguity counts (D2) | guard on the required section; `npm test` |
| REQ-003 | `spec.md` self-review gains the **decision read-back**: the brief's `## Decisions locked` table *and* the register entries stage 2 recorded for rejected alternatives (`brainstorm.md:105`). A contradiction is resolved out loud, never silently (D3) | guard: `spec.md` names both sources; review for the prose |
| REQ-004 | `spec.md` self-review gains the **cost checkpoint**: print surfaces / guards / REQ count as of stage 2 and as of now. **Prints; never narrows.** The stage-3 gate is manual, so the operator decides (D4) | guard on the item; the printed delta appears in the Self-review section |
| REQ-005 | `planning.md` self-review gains **"every command, path and file a DoD names resolves"** (D1/D5 at stage 4) | guard on the item; probed |
| REQ-006 | `planning.md` requires the same committed **`## Self-review`** section (D2) | guard; `npm test` |
| REQ-007 | `learned.md`'s stage map lists rule 14 at **stages 3 and 4**, not only 9 — the read-back made structural (D5) | guard comparing the stage map against the rule's own text; probed |
| REQ-008 | `references/stages.md` §3 and §4 gate criteria demand the `## Self-review` section and name what it must contain | the existing cross-surface stage guard + review |
| REQ-009 | Every new guard has a negative self-test in `.github/workflows/validate.yml`; `test/negatives.py`'s `MIN_EXPECTED` recomputed from the workflow | `npm run test:all` green |
| REQ-010 | Propagation walked: `CHANGELOG.md`, `CONTRIBUTING.md` → *The invariants* for each new guard, `cursor/rules/task-pipeline.mdc` (**this changes how an agent behaves elsewhere** → `review`), `templates/` if a template gains the section | `npm test` reach and citation guards |
| REQ-011 | Four-way version sync at **1.12.0** | the four-way version guard |

## Decisions locked (the grill's output)

| # | Decision | Chosen | Rationale |
|---|---|---|---|
| D1 | How many defects this run takes | All five | Four of them are one shape; fixing four and leaving the fifth is the *"fix scoped to its instance"* failure this repo already has two retro entries about |
| D2 | What trace the self-review leaves | A short `## Self-review` section **committed in the document itself** | It lives beside the artifact, survives compaction, is readable at the gate and at stage 10. Exactly the principle `planning.md` already applies to the set difference |
| D3 | What the cost checkpoint does when growth is large | **Prints the numbers; the operator decides.** No threshold, no auto-stop | An agent that may narrow the task on its own judgement violates *"never narrow the task silently"*. A made-up threshold either fires on noise or never fires |
| D4 | Where the cost checkpoint lives | Stage 3, not stage 0 | The surface count is unknowable at intake and knowable once the spec is written |
| D5 | Whether to rewrite the two files | No — add only | Both are accurate. The defects are absences |

## Autonomy (the sweep — stages 1→10 read this instead of asking)

| Row | Answer |
|---|---|
| Branch | `spec-plan-quality`, off `main`. Public-contract change → PR |
| Commits | Conventional; the shipping commit appends `; v1.12.0` |
| Test command | `npm test`; before any tag, `npm run test:all` |
| Lint | None separate — the validator is the lint |
| Docs sources | Internal doctrine only; stage 1 is expected to be thin and must say so rather than manufacture work |
| Deploy target | npm `task-pipeline-skill` + GitHub release via tag `v1.12.0` |
| Deploy authorization | **Intent is the full cycle. Not pre-granted here** — stage 7's gate is `manual` by construction, so the authorization happens there, in view of what actually shipped |
| Post-deploy | `npm view task-pipeline-skill version`, the workflow smoke test, then `npx --yes sshlg-skills@latest update` |
| Docs targets | `CHANGELOG.md`, `CONTRIBUTING.md`, `cursor/rules/task-pipeline.mdc`, `templates/` if touched |
| Wiki target | `projects/task-pipeline/concepts/` — a spec/plan-quality concept note |
| Graph | `graphify-out/` exists → refresh at stage 9 + divergence check |
| Model | Opus 5, whole run, no per-stage overrides |
| Loop mode | Off — no `pipeline.json` in this repo |
| UI verdict | **Not user-facing.** Doctrine prose and validator guards; this repo has no `docs/ux/`. Restated and overridable at stage 2 |

## Done-criteria

- Every REQ closed with evidence from a check **seen failing once** against a
  planted defect, with the plant proven to have landed first (R-001);
- `npm run test:all` green on the commit any tag points at;
- the carry-over ledger has no unresolved row, its count printed beside every gate
  verdict;
- **this run's own stage 3 and stage 4 obey the doctrine they are adding** — the
  spec and the plan each carry a real `## Self-review` section with computed
  numbers. A change to the self-review that its own run does not perform is the
  `default-routing-adoption` retro entry repeating;
- the retrospective written last: prune → stamp → entry.

## Open assumptions / risks

- **A1 — the guards can only check that the doctrine says it.** `validate.py`
  validates this repository; it cannot prove a foreign run performed a self-review.
  Every REQ here is therefore "the file carries the item", and the real enforcement
  is the stage gate. This must be said plainly in the spec rather than implied, or
  this run reproduces D1 while fixing D1.
- **A2 — D5 has no incident.** Found by reading. Recorded as weaker evidence than
  the other four; kept because it is the same class as D1 and free to fix alongside.
- **A3 — the `## Self-review` section is ceremony if it becomes a template to fill
  with zeroes.** The mitigation is that every line carries a **computed number**, not
  a tick, and a number nobody computed is visible as a number nobody computed. Stage
  2 must confirm this is enough, because no check can decide it.
