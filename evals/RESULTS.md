# Evaluation results — task-pipeline

**Status: the suite is authored. One run is recorded and it was self-observed by the
author; no blind run has been made on any model.** Recorded this way rather than left
blank, because an empty results file and an unrun suite look identical, and this
repository's own doctrine calls that the failure — a skip is not a pass.

**The numbers below are computed, not asserted.** `python3 evals/run.py` counts the
suite and the dated run headings in this file. A value typed here that disagrees with
what it prints is the defect, and it is the document that is wrong — this file said
*"has not been executed"* and *"Dated runs recorded 0"* for five releases while the
tool beneath it printed `recorded runs: 1`, which is the self-contradiction canon 2
exists to prevent, in the one file whose whole job is honesty about evidence.

Running these needs a fresh session per query, per model. That is a human or agent
step; `evals/run.py` prints the protocol and deliberately never reports a pass it
did not observe.

## How to record a run

One table per date + model. Verdict is `pass` / `fail` / `partial`, and a `fail`
carries what actually happened, not a shrug.

```markdown
## 2026-08-10 · sonnet

| id | verdict | what happened |
|---|---|---|
| TRIG-01 | pass | harvest ran first, ledger written, no code before the brief |
| NOTRIG-02 | fail | invoked the skill for a one-character README fix |
```

Then act on the result the way the enterprise guidance says: declining trigger
accuracy → change the description; coexistence conflicts → narrow it or consolidate;
persistent instruction-following failures → the instruction is not prominent enough,
or it belongs in a check.

## Ratchet

| Metric | Value | Computed by | As of |
|---|---|---|---|
| Evals authored | 15 | `python3 evals/run.py` → `suite: N evals` | 2026-08-08 |
| Categories covered | 5 of 5 | the suite's own `category` fields | 2026-08-08 |
| Dated runs recorded | **1** | `python3 evals/run.py` → `recorded runs: N` | 2026-08-08 |
| …of those, **blind** | **0** | run headings not marked `self-observed` | 2026-08-08 |
| Models exercised blind | **0 of 3** | distinct models across blind runs | 2026-08-08 |

**The last three rows are the honest state of this skill's behavioural evidence**, and
the split matters more than the total: a run the author watched, knowing the expected
behaviour, is an observation of instruction-following and not an evaluation. Collapsing
the two into one "runs recorded" number is how a self-check gets quoted as a result.

That split is **canon 5 applied to evaluation** — *green nobody watched turn red is not
evidence* ([`documentation.md`](../plugins/task-pipeline/skills/task-pipeline/references/documentation.md)
→ *The canons*). A self-observed run is a green the author was steering; a blind run is
the only one that could have come back red for a reason nobody arranged. The code graph
surfaced this link before any document stated it, which is the divergence check earning
its keep.

Everything else in this repository is proven by structural guards — the count is
whatever `npm run test:all` prints, deliberately not restated here — and those check
the *form*. These are the only checks that speak to the *behaviour*. Printed here so a
green structural suite is never read as "the skill is known to work".

## Runs

Newest first. Each entry states the model, the task, and how the evidence was
obtained — a self-observed run and a blind one are not the same claim.

## 2026-08-03 · opus · self-observed, not a blind run

**Scope of this evidence.** The author ran the skill on a real task
(`default-routing-adoption`) and watched it follow its own doctrine. That is a
legitimate observation of instruction-following and **not** an independent
evaluation: the operator knew the expected behaviour and the same person wrote both
sides. It closes none of the trigger-accuracy or coexistence rows, which need fresh
sessions and a reader who is not the author.

| id | verdict | what happened |
|---|---|---|
| INSTR-01 | pass | harvest ran before the first question; source ledger written into the brief; doc inventory answered (`DOCMAP.md` absent → seeded this run); intent reconciled against as-built (clean, in sync) |
| INSTR-04 | partial | the ladder walk and the evidence rule ran at stage 10, but a stage-10 self-audit by the author is the weakest form of the check |
| others | not run | require fresh sessions per model |

**One divergence worth recording:** at stage 5 the work contradicted the spec —
inventory showed this repository already had a gate over the same corpus, so seeding
a second one would have violated the SSOT rule the doc map publishes. The finding
went back to stage 3, the spec was revised, and the changed check was raised in the
carry-over ledger for the operator rather than swapped silently. The loop behaved as
designed.

