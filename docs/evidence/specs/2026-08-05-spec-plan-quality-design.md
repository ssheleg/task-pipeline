# Design — spec and plan quality: the read-back

**Run:** `spec-plan-quality` · 2026-08-05 · brief:
`docs/superpowers/specs/2026-08-05-spec-plan-quality-brief.md`

Five defects, one mechanism. In four of the five the rule already exists in this
bundle and lives in a stage that never hands it to the stage which would act on it.
The fix is a **read-back**: the stage that must obey a rule is told to go and read
it. The fifth is a genuine absence — nothing anywhere asks whether a change still
costs what it was worth.

**This design adds; it rewrites nothing.** `spec.md` and `planning.md` are accurate.
Their problem is what they omit.

## Contents

- Global constraints
- Contract 1 — the `## Self-review` section
- Contract 2 — spec.md's four new items
- Contract 3 — planning.md's two new items
- Contract 4 — learned.md's stage map
- Contract 5 — stages.md gate criteria
- Contract 6 — guards and negative tests
- Contract 7 — propagation and version
- What this design deliberately does not do
- Verification
- Self-review

## Global constraints

Stages 4 and 5 consume this block verbatim.

- Prose wraps at ~80 columns; no wrapped line begins with `>`.
- `npm test` green after **every** task; `npm run test:all` before any tag.
- **The hygiene gate runs in diff mode after every task** — it shipped in v1.12.0
  and this is the first run that must obey its own doctrine.
- Corrupt fixtures in **Python**, never `sed -i`.
- R-001: prove a plant landed in the parsed text before touching a silent check.
- R-002: any error in a batch → re-verify every edit in that batch.
- **R-003 (new, and it binds this run):** when you fix a defect in one check, run
  that defect's definition against its siblings before moving on. `spec.md` and
  `planning.md` are siblings; an item added to one is a question asked of the other.
- Every reference over 100 lines keeps its `## Contents` list in step with its
  headings.
- No hardcoded vendor model ids.

## Contract 1 — the `## Self-review` section

Both stage artifacts gain a **committed** section, last before the gate. Every line
carries a **computed number, not a tick** — a number nobody computed is visible as
a number nobody computed, which a checkbox never is.

Shape, identical in both files so one habit covers both:

```markdown
## Self-review

- REQ coverage: <n> in brief, <n> covered, difference <set or ∅>
- Named checks: <n> named, <n> resolve, <n> marked `review`
- Decisions: checked against <the brief's D-table> and <stage 2's rejected options> — <verdict>
- Cost: <surfaces>/<guards>/<REQ> now, <…> at stage 2 — <proportionate | grown, and why>
- Hygiene: <n> checks, <n> findings, <n> open
- Placeholders: <n> · Ambiguity: <n> found, <n> resolved inline
```

The section is written **before** the gate is presented, and the gate presents it.

## Contract 2 — spec.md's four new items

Appended to `## Self-review — before showing it`, keeping its existing six.

**7. Every check this spec names resolves.** Walk the *Verification* table and every
sentence that says how something is proven. For each: does that check exist today,
or is it being built by this plan? A check that is neither is **not** a verification
— mark it `review` and say so, or build it. *(D1. This repository's whole doctrine
is that a green from a check nobody watched fail is not evidence; stage 3 is where
checks are first named, and nothing here asked whether the named one is real.)*

**8. Read the decisions back.** Open the brief's `## Decisions locked` table and the
register entries stage 2 recorded for **rejected** alternatives
(`references/brainstorm.md` → *The approved design is a set of decisions*).
Does any contract in this spec contradict one? A contradiction is resolved **out
loud** — amend the spec, or reverse the decision and record the reversal. Never
silently. *(D3. `brainstorm.md` already requires rejected options to be recorded,
and nothing at stage 3 ever reads them.)*

**9. Print the cost.** Count the surfaces this spec touches, the guards it adds, and
the REQ rows now versus at stage 2. **Print all three; decide nothing.** Growth is
information for the operator, whose gate this is — an agent that may narrow the task
on its own judgement breaks *never narrow the task silently*. *(D4, and the only one
of the five that is a genuine absence rather than a stranded rule.)*

**10. Run the hygiene gate** over what this stage wrote, and record its counts in the
`## Self-review` section. *(v1.12.0.)*

## Contract 3 — planning.md's two new items

Appended to `## Self-review — before handing off`, keeping its existing six.

**7. Every command, path and file a DoD names resolves.** Walk each task's
*Definition of done* and its steps. A DoD that says `npm run lint:paths` when no such
script exists is an instruction the implementer cannot follow and a check the
acceptance cannot run. *(D1/D5. `learned.md` rule 14 — every target resolvable — has
existed since v1.4.0 and fires only at stage 9, four stages after the target is
written.)*

**8. Run the hygiene gate** over what this stage wrote, and record its counts in the
`## Self-review` section.

**And the same `## Self-review` section as contract 1**, with the same six lines.

## Contract 4 — learned.md's stage map

The map at `references/learned.md` lists rule 14 under *9 Docs* only. Extend:

```
| 3 Spec | 14 — every check the spec names must resolve, at the moment it is named |
| 4 Plan | 14 — every command, path and file a DoD names must resolve |
```

The row for *9 Docs* stays. A rule can bind more than one stage, and this one always
did — nobody had written it down where it would be read.

## Contract 5 — stages.md gate criteria

- **§3 GATE (manual)** — add: *the `## Self-review` section is written and committed
  with computed values; every check the spec names resolves or is marked `review`;
  the brief's decisions and stage 2's rejected options read back with no unresolved
  contradiction; the cost delta printed*.
- **§4 GATE (auto)** — add: *the `## Self-review` section is written with computed
  values; every command, path and file a DoD names resolves*.

## Contract 6 — guards and negative tests

Three guards, one per surface that can be checked mechanically **in this
repository**:

1. `references/spec.md` contains items 7–10 and the `## Self-review` shape.
2. `references/planning.md` contains items 7–8 and the same shape.
3. `references/learned.md`'s stage map names rule 14 at stages 3 and 4.

Each gets a negative self-test in `.github/workflows/validate.yml` with a **unique
`rm -rf`-guarded scratch directory** (v1.12.0's rule), and `MIN_EXPECTED` is
recomputed from the workflow.

**A1, said plainly rather than implied:** these guards prove the doctrine files
*carry* the items. Nothing here can prove a run in someone else's repository
performed a self-review — `validate.py` validates this repository. The real
enforcement is the stage gate, and saying so is the point: a run that claimed
otherwise would reproduce D1 while fixing D1.

## Contract 7 — propagation and version

Four-way sync to **1.13.0**. `CHANGELOG.md` written as what changed and why it
mattered — the diagnosis (four of five are one shape), and that the cost checkpoint
prints rather than decides. Plus `README.md`, `CONTRIBUTING.md` → *The invariants*
for the new guards, `references/portability.md` manifest, and
`cursor/rules/task-pipeline.mdc` (**`review`**, self-contained, no relative links).

## What this design deliberately does not do

- **Does not touch `grill.md`.** D4 lands at stage 3, where the surface count is
  knowable; at stage 0 it would ask for a number that does not exist yet. Recorded
  as C-002, a known exclusion.
- **Does not invent a numeric threshold** for the cost checkpoint.
- **Does not rewrite** either file's existing items.
- **Does not add a guard for whether a foreign run obeyed the doctrine.** Impossible
  here, and pretending otherwise is the defect being fixed.

## Verification

| REQ | Verified by |
|---|---|
| REQ-001 | guard 1, probed by deleting item 7 from a scratch copy |
| REQ-002 | guard 1, probed by deleting the `## Self-review` shape |
| REQ-003 | guard 1 (item 8 present); the read-back's *content* is `review` |
| REQ-004 | guard 1 (item 9 present) |
| REQ-005 | guard 2, probed |
| REQ-006 | guard 2, probed |
| REQ-007 | guard 3, probed by removing the stage-3/4 rows from the map |
| REQ-008 | the existing cross-surface stage guard for gate **type**; the criteria prose is `review` |
| REQ-009 | `npm run test:all` green; `MIN_EXPECTED` recomputed from the workflow |
| REQ-010 | `npm test` reach and citation guards; Cursor rule `review` |
| REQ-011 | the four-way version guard |

## Self-review

- **REQ coverage:** 11 in brief, 11 covered, difference ∅.
- **Named checks:** 11 named. **8 mechanical**, each naming a guard this plan builds
  or one that exists. **3 marked `review` on purpose** — the read-back's content
  (REQ-003), the gate-criteria prose (REQ-008), the Cursor rule (REQ-010). None is
  asserted as mechanical.
- **Decisions:** read back against the brief's D1–D5 and its *Out of scope* list. No
  contradiction. D4 said the checkpoint prints and never narrows; contract 2 item 9
  says exactly that. The brief excluded `grill.md`; nothing here touches it.
- **Cost:** 8 surfaces, 3 guards, 11 REQ. At stage 0 the estimate was "two doctrine
  files plus a reach fix" — 8 surfaces is the propagation those two files oblige, not
  growth in the change itself. **Proportionate.**
- **Hygiene:** 6 checks, 0 findings, 0 open.
- **Placeholders:** 0 · **Ambiguity:** 1 found and resolved inline — item 9's "print
  the cost" now names the three numbers rather than saying "the cost".
