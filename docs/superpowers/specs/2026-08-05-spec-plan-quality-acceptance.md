# Acceptance — spec and plan quality: the read-back

**Run:** `spec-plan-quality` · 2026-08-05 · v1.13.0

Carry-over at close: **5 rows, 0 unresolved.**

## Ladder walk

| Seam | Absence | Became |
|---|---|---|
| decision → spec | Nothing read the brief's `Decisions locked` table back at stage 3, though `brainstorm.md` had always required rejected options be recorded | REQ-003, shipped |
| contract → its check | A spec could name a check that does not exist, and nothing asked | REQ-001, shipped |
| task → executed test | A DoD could name a command that does not exist; rule 14 caught it four stages later | REQ-005 + REQ-007, shipped |
| self-review → artefact | *"Self-review passed"* was unfalsifiable | REQ-002 + REQ-006, shipped |
| scope → worth | No stage asked whether the change had outgrown its value | REQ-004, shipped — **printing, never deciding** |
| **guard → foreign run** | **None of these guards can prove a run in another repository obeyed the doctrine** | Not an absence to fix — a boundary to state. Said in the spec, the guard's comment and the CHANGELOG |

## Coverage

| REQ | Verdict | Evidence — from a check seen failing once |
|---|---|---|
| REQ-001 | ✅ | Guard 1. **Plant-before-guard honoured:** item 7 removed from a scratch copy → `npm test` **passed**, proving the guard absent; written, it caught the same plant naming the file. Negative self-test *(the spec must keep asking whether a named check is real)* |
| REQ-002 | ✅ | Negative self-test *(the self-review must leave a committed trace)* — removes `computed number, not a tick` |
| REQ-003 | ✅ / ⚠️ | Guard 1 proves item 8 is present. **The read-back's *content* is `review`** — no check can decide whether a contradiction was actually resolved |
| REQ-004 | ✅ | Guard 1 proves item 9 is present. Its *judgement* is deliberately the operator's: it prints three numbers and decides nothing |
| REQ-005 | ✅ | Guard 2 + negative self-test *(a plan must keep asking whether a DoD's targets resolve)* |
| REQ-006 | ✅ | Guard 2 — the same section shape, checked in both files |
| REQ-007 | ✅ | Guard 3 + negative self-test *(rule 14 must bind the stages that write the targets)*, planted by unmapping stage 3 |
| REQ-008 | ✅ / ⚠️ | The cross-surface stage guard checks gate **types**; the criteria **prose** is `review`, as it is for every other criterion in `stages.md` |
| REQ-009 | ✅ | `python3 test/negatives.py` → **all 80 guards provably reject their planted defect** (76 → 80). Floor recomputed from the workflow |
| REQ-010 | ✅ / ⚠️ | CHANGELOG, README map, CONTRIBUTING (citing a literal `validate.py` prints), portability, SKILL-CARD — all green under `npm test`. **Cursor rule `review`**: updated, 0 relative links, verified by eye |
| REQ-011 | ✅ | Four-way sync at 1.13.0 |

**11 REQ · 8 verified by a proven check · 3 carrying an explicit `review` half.**

## This run obeyed the doctrine it added

The done-criteria demanded it, because a change to the self-review that its own run
does not perform is the `default-routing-adoption` retro entry repeating.

- The **spec** carries a `## Self-review` with computed values — 11/11 REQ, 8
  mechanical checks and 3 marked `review`, decisions read back against D1–D5 with no
  contradiction, cost printed (8 surfaces / 3 guards / 11 REQ), hygiene 6/0/0.
- The **plan** carries one too — set equality verified mechanically, 6 named commands
  all resolving, cost 10/3/11 with the two extra surfaces named as propagation rather
  than growth.
- The **hygiene gate** (v1.12.0) ran in diff mode after every task. It failed to run
  once, from the wrong directory, and that was corrected out loud rather than skipped.

## Ratchets

| Ratchet | Before | After |
|---|---|---|
| Negative self-tests | 76 | **80** |
| Standing instructions | 3 of 10 | 3 of 10 |
| Hygiene floors | 0×6 | 0×6 |
| Models exercised by the eval suite | 0 of 3 | 0 of 3 — unchanged, still the honest state |

## Sign-off

Operator authorised the run to completion ("вперед"). Carry-over 0 unresolved.
