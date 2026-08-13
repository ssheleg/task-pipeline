# Task brief — artifact hygiene: the defects an agent leaves behind

**Run:** `artifact-hygiene` · 2026-08-05 · model: Opus 5 (top tier available,
confirmed at preflight, no per-stage overrides)

A shipped, executable gate that finds the defect class an agent produces and no
existing check looks for: conflict markers, surviving placeholders, unterminated
code fences, truncation stubs, duplicated blocks from a half-applied edit, and
sections started and abandoned.

Sibling of `templates/docgate.sh`, not a section inside it: that gate's own `SCOPE`
header excludes code, and hygiene needs code — `<<<<<<<` and
`// ... existing code ...` live there.

## Contents

- Knowledge sources
- The six checks
- Measured baseline
- Scope
- Requirements (the REQ spine)
- Decisions locked
- Autonomy
- Done-criteria
- Open assumptions / risks

## Knowledge sources (the phase-1 harvest — written BEFORE the first question)

| Source | What it says about this task | Fresh? |
|---|---|---|
| `templates/docgate.sh` (499 lines) | **The model, read in full at the contract level.** `SCOPE:` header naming what it does *not* check · `EXIT CODE IS THE OUTPUT`, VERDICT last and nothing after it · portable to macOS bash 3.2 (no `grep -P`, `sed -i`, `readarray`, `mapfile`) · **progressive arming** — a section with no input prints `dormant` and stays green · ratchet floors that may only fall · env-overridable paths · a final line of computed numbers | current — and every one of those contracts binds the sibling |
| `test/validate.py` | **Zero hygiene guards.** `FENCE_RE` exists only to *exclude* fenced code from other checks. No placeholder scan, no conflict-marker scan, no truncation scan, no duplicate-block scan | current — the category is empty, not weak |
| `CLAUDE.md` → *Commands* | `npm test` already **executes** `docgate.sh` over a scratch project seeded from the templates and requires exit 0. The precedent for shipping a runnable gate and dogfooding it is established | current |
| `docs/superpowers/retro.md` → **R-002** | *"When a batch of edits returns any error, re-verify every edit in that batch."* Its incident: two edits issued together, the second failed and was retried, **the first was silently never applied**, reported done, shipped in v1.7.0. **Check 5 is the mechanical version of this standing instruction** | current — the strongest motivation in the file |
| `references/learned.md` | Rules 8 and 14 — every number computed, every target resolvable — are the same family: claims nobody checks | current |
| `references/gates.md` | Gate anatomy, the probe recipe, ratchet floors, where a gate runs. The doctrine this new gate must be written against | current |
| `docs/DOCMAP.md:44` | Rows that fire: *a new document, rule or guard* · *a new or changed guard* · *a user-visible capability, install path or stage* | current |
| Measured baseline (below) | Computed on this tree, not estimated | 2026-08-05 |

## The six checks

| # | Check | The agent failure it catches |
|---|---|---|
| 1 | Conflict markers — `<<<<<<< `, `=======`, `>>>>>>> ` | a merge left half-resolved |
| 2 | Surviving placeholders — `TODO` / `TBD` / `FIXME` / `XXX` | a stub that outlived the task |
| 3 | Unterminated code fence — odd fence count in a markdown file | generation cut off mid-block |
| 4 | Truncation stubs — `... existing code ...`, `[TRUNC`, `rest of the file unchanged` | the agent "shortened" a file while rewriting it |
| 5 | **Duplicated adjacent block** | **the R-002 signature** — a batch where one edit applied twice, or where a retry duplicated instead of replacing |
| 6 | Heading with no body | a section opened and abandoned |

Check 5 is the one worth the whole run: it turns a standing instruction that
currently depends on the agent's diligence into something a machine decides.

## Measured baseline

Computed over 94 tracked files (excluding `graphify-out/`), 2026-08-05:

| Check | Found today | Read |
|---|---|---|
| 1 conflict markers | **0** | clean |
| 2 placeholders | **32 occurrences in 16 files** | **almost all legitimate** — see A1 |
| 4 truncation stubs | **0** | clean |
| 3, 5, 6 | not measurable with a one-line probe | stage 2 measures them before specifying them |

## Scope

**In:**

- `templates/hygiene.sh` — a new shipped, seeded, executable gate carrying every
  contract `docgate.sh` carries, verified by the same guards;
- the six checks, each with its false-positive surface named in the script's own
  `SCOPE` header;
- **two modes:** the run's diff at zero tolerance, the whole tree behind a ratchet
  floor;
- doctrine wiring: the gate runs after **each stage-5 task**, and again at stages 6
  and 9;
- the obligation to **fix** what it reports, written into stage-5 doctrine — the
  script never edits;
- `npm test` executing it over a seeded scratch project, as it already does for
  `docgate.sh`;
- the propagation surfaces the matrix names.

**Out:**

- **auto-fixing.** Decided below (D3). None of the six is safely machine-fixable:
  deleting a "duplicated block" sometimes deletes a legitimate repetition, and
  deleting a `TODO` erases a reminder instead of discharging it;
- linting code style, formatting, spelling, or anything a language's own linter
  owns. This gate is about defects with an *agent* signature;
- changing `docgate.sh`. It stays as it is.

## Requirements (the REQ spine — every later stage traces to these IDs)

Frozen at stage 0. Adding is free; removing needs the operator's explicit word.

| id | Requirement | Verified by |
|---|---|---|
| REQ-001 | `templates/hygiene.sh` exists and carries the full `docgate.sh` contract: `SCOPE:` header, VERDICT last, bash-3.2 portability, progressive arming, computed final line | the existing template guards, extended to the new file; probed |
| REQ-002 | Check 1 — conflict markers | probed with a planted marker, plant proven to land first (R-001) |
| REQ-003 | Check 2 — placeholders, **with the false-positive surface solved** (A1) and the solution stated in `SCOPE` | probed both ways: a real placeholder fails; this repo's own doctrine prose does not |
| REQ-004 | Check 3 — unterminated fence | probed |
| REQ-005 | Check 4 — truncation stubs | probed |
| REQ-006 | Check 5 — duplicated adjacent block, the R-002 mechanisation | probed with a planted duplicate |
| REQ-007 | Check 6 — heading with no body | probed |
| REQ-008 | Two modes: diff at zero tolerance, tree behind a floor set to today's measured count | the floor is a computed number in the verdict line, not a literal from this brief |
| REQ-009 | Doctrine: `build.md` runs it after each task; `stages.md` §5, §6 and §9 name it in their gate criteria; `gates.md` gains it as a worked example | cross-surface stage guard + review |
| REQ-010 | The **fix obligation** is doctrine: a finding is fixed or explicitly carried over; the script never edits | review — no check can decide it |
| REQ-011 | `npm test` executes the gate over a seeded scratch project and requires exit 0 | `npm test` |
| REQ-012 | A negative self-test per check in `.github/workflows/validate.yml`; `MIN_EXPECTED` recomputed from the workflow | `npm run test:all` |
| REQ-013 | Propagation: `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md` invariants, `templates/README.md`, `references/artifacts.md`, `references/portability.md`, `cursor/rules/task-pipeline.mdc` (`review`) | `npm test` reach, manifest and citation guards |
| REQ-014 | Four-way version sync at **1.12.0** | the four-way version guard |

## Decisions locked (the grill's output)

| # | Decision | Chosen | Rationale |
|---|---|---|---|
| D1 | Own script or a docgate section | **Own script**, sibling | `docgate.sh`'s `SCOPE` excludes code; hygiene requires it. Extending it would break the contract its own validator enforces |
| D2 | What it scans | **Diff at zero tolerance + whole tree behind a ratchet floor** | Zero tolerance for what this run wrote; a floor so an existing repository can adopt the gate without starting red, while nothing new is forgiven |
| D3 | Fix automatically or report | **Reports with `file:line`; the agent fixes** | None of the six is safely machine-fixable. The obligation to act becomes doctrine (REQ-010) rather than a silent rewrite |
| D4 | Where it runs | **After each stage-5 task, plus stages 6 and 9** | A defect from task 2 of 8 found after task 8 is fixed by an agent that no longer remembers the code. Per-task costs one fast diff scan |
| D5 | The check list | The six above; additions free | "и тд" in the request delegates the enumeration; six is what the evidence supports today |

## Autonomy (the sweep — stages 1→10 read this instead of asking)

| Row | Answer |
|---|---|
| Branch | `artifact-hygiene`, off `main`. Public-contract change → PR |
| Commits | Conventional; the shipping commit appends `; v1.12.0` |
| Test command | `npm test`; before any tag, `npm run test:all` |
| Lint | None separate — the validator is the lint |
| Shell portability | **macOS bash 3.2.** No `grep -P`, `sed -i`, `readarray`, `mapfile`. Corrupt fixtures in Python, never `sed -i` |
| Deploy target | npm `task-pipeline-skill` + GitHub release via tag `v1.12.0` |
| Deploy authorization | Intent is the full cycle. **Not pre-granted** — stage 7's gate is `manual` by construction |
| Post-deploy | `npm view task-pipeline-skill version`, the workflow smoke test, then `npx --yes sshlg-skills@latest update` |
| Docs targets | Per REQ-013 |
| Wiki target | `projects/task-pipeline/concepts/` — a hygiene-gate concept note |
| Graph | `graphify-out/` exists → refresh at stage 9 + divergence check |
| Model | Opus 5, whole run, no per-stage overrides |
| Loop mode | Off — no `pipeline.json` in this repo |
| UI verdict | **Not user-facing.** A shell gate and doctrine prose; this repo has no `docs/ux/`. Restated and overridable at stage 2 |
| Parked work | The `spec-plan-quality` run waits at its stage-0 gate on branch `spec-plan-quality`, commit `dd3155e`. Stage 10 unparks it |

## Done-criteria

- Every REQ closed with evidence from a check **seen failing once** against a
  planted defect, with the plant proven to have landed first (R-001);
- `npm run test:all` green on the commit any tag points at;
- the gate runs green on this repository, with its floor printed as a computed
  number;
- the carry-over ledger has no unresolved row, its count printed beside every gate
  verdict;
- the retrospective written last: prune → stamp → entry.

## Open assumptions / risks

- **A1 — the placeholder check's false-positive surface, and this repository is its
  worst case.** Measured: 32 occurrences of `TODO`/`TBD`/`FIXME`/`XXX` across 16
  files, and the great majority are **legitimate mentions** — this is a doctrine
  repository whose `planning.md` literally contains the line
  `- "TBD", "TODO", "implement later", "fill in details"` as a list of things never
  to write. Stripping fenced code does not solve it, because that line is prose in
  quotes. **Distinguishing *using* a placeholder from *naming* one is the hardest
  part of this run**, it is stage 2's first job, and a check that cannot make the
  distinction should ship dormant rather than noisy.
- **A2 — checks 5 and 6 are unmeasured.** "Duplicated adjacent block" and "heading
  with no body" need a real definition before their false-positive rate is knowable
  (a changelog legitimately repeats structure; a heading may be an intentional
  index). Stage 2 measures both on this tree **before** specifying them, per
  `gates.md`' rule that a detector is measured before it ships.
- **A3 — per-task execution must stay fast.** A diff-scoped scan after each stage-5
  task is on the critical path of the build loop. If it is not fast, agents will be
  tempted to skip it, which is how a gate becomes decoration.
