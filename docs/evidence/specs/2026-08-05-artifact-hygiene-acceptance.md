# Acceptance — artifact hygiene

**Run:** `artifact-hygiene` · 2026-08-05 · v1.12.0 · merged as `13028e9`

Carry-over at close: **7 rows, 1 unresolved** (C-004, discharged below).

## Ladder walk — what was never written

Walked each REQ bottom-up (decision → spec section → contract and its failure
behaviour → task → change → executed test → surface). Findings ordered by seam.

| Seam | Absence found | Became |
|---|---|---|
| contract → failure behaviour | Check 4's false-positive surface was never asked about, though check 2's had been. The gate found it by running | closed in-run (C-005); the class is the retro's R-003 below |
| change → executed test | The VERDICT-last guard had no probe, so nobody knew it was decorative | closed in-run (C-006) |
| change → executed test | Scratch-directory uniqueness had no check, and four collisions predated the branch | closed in-run; guard + negative test added |
| surface → docs | `templates/README.md`, `artifacts.md`, `portability.md` did not know the new template existed | closed at stage 9 by the existing reach guards, which fired |
| **artefact structure** | **A blank line split the carry-over ledger's own table in two.** A markdown-structure defect, in the run whose subject is exactly that class — **and the gate does not catch it** | **REQ-015, below: recorded as backlog, not silently fixed** |

## Coverage

| REQ | Verdict | Evidence — from a check seen failing once |
|---|---|---|
| REQ-001 | ✅ | The template contract guards iterate `GATE_SCRIPTS`. Probed: removing `SCOPE:` from `hygiene.sh` → validator rejects, naming the file |
| REQ-002 | ✅ | Negative self-test *(conflict markers)*; plant asserted present before the exit code was read |
| REQ-003 | ✅ | Negative self-test *(a surviving placeholder)*. Measured 0 on 99 files **after** the definition moved from lexical to positional |
| REQ-004 | ✅ | Negative self-test *(an unterminated fence)* |
| REQ-005 | ✅ | Negative self-test *(a truncation stub)*, anchored line-leading after it fired on this run's own documents |
| REQ-006 | ✅ | Negative self-test *(a duplicated adjacent block)* — the R-002 mechanisation |
| REQ-007 | ✅ | Negative self-test *(an empty section)*. Two real findings fixed rather than floored, so it ships at 0 |
| REQ-008 | ✅ | Verdict line prints six counts and their floors; both modes exercised. Diff mode's zero tolerance is structural — `floor_for` returns 0 when `MODE=diff` |
| REQ-009 | ✅ | `build.md` §*The hygiene gate*, `stages.md` §5/§6/§9, `artifacts.md`, `portability.md`, `templates/README.md`. `npm test` green over all of them |
| REQ-010 | ⚠️ **`review`** | *"The agent fixes, the script never edits"* is doctrine. **No check can decide whether an agent acted on a finding**, and this is stated rather than dressed up as coverage |
| REQ-011 | ✅ | `npm test` executes the gate over a clean scratch project, requires exit 0 **and** all six counts reported. Probed: a gate made red on clean seeds is rejected |
| REQ-012 | ✅ | `python3 test/negatives.py` → **all 76 guards provably reject their planted defect** (68 → 76). Floor recomputed from the workflow |
| REQ-013 | ✅ / ⚠️ | CHANGELOG, README, CONTRIBUTING, SKILL-CARD, portability, artifacts, templates/README all green under `npm test`. **The Cursor rule is `review`** — the matrix marks it so because no check can decide whether a change alters agent behaviour in a foreign project. Verified by eye: updated, 0 relative links |
| REQ-014 | ✅ | Four-way sync at 1.12.0; release workflow `success`; `npm view task-pipeline-skill version` → **1.12.0**; local plugin → 1.12.0, no shadowing plain copies |
| **REQ-015** | 🔵 **backlog, printed not buried** | *New, from the ladder walk.* A blank line inside a markdown table silently splits it. The hygiene gate has no check for broken table structure. **Not fixed in this run** — a seventh check is worth measuring before it is written, which is the rule this run just demonstrated twice. Carried as the gate's own first backlog row |

## Axis rotation

Findings this run split **5 new / 3 self-inflicted**. The three self-inflicted —
check 4 repeating check 2's mistake, the guard placed after the verdict, the guard
firing on its own test — all arrived while *building the detector*, not while
searching. The searching axis (measure each definition against the tree) was
productive throughout and was not exhausted; no rotation was needed.

## Ratchets

| Ratchet | Before | After |
|---|---|---|
| Negative self-tests | 68 | **76** |
| Hygiene floors (6 checks) | — | **0, 0, 0, 0, 0, 0** |
| Standing instructions | 2 of 10 | **3 of 10** |
| Models exercised by the eval suite | 0 of 3 | 0 of 3 — unchanged, and still the honest state |

## Gate verdicts

- `npm test` — PASS · carry-over 1 unresolved at the time
- `npm run test:all` — **76/76 guards provably reject their plant** · carry-over 1
- hygiene gate on `main` — `conflict 0 · placeholder 0 · fence 0 · truncation 0 ·
  duplicate 0 · empty-section 0` · carry-over 1
- CI on the PR — both `validate` jobs pass
- release workflow — `success`; npm 1.12.0

## Sign-off

Operator authorised the full cycle ("закрывай все до конца") after reviewing the
stage-7 report. Merged, tagged, released, published, local copies refreshed, graph
and wiki synced.
