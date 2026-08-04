# Evaluation results — task-pipeline

**Status: the suite is authored and has not been executed.** Recorded here rather
than left blank, because an empty results file and an unrun suite look identical,
and this repository's own doctrine calls that the failure — a skip is not a pass.

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

| Metric | Value | As of |
|---|---|---|
| Evals authored | 15 | 2026-08-03 |
| Categories covered | 5 of 5 | 2026-08-03 |
| Models exercised | **0 of 3** | 2026-08-03 |
| Dated runs recorded | **0** | 2026-08-03 |

The bottom two numbers are the honest state of this skill's behavioural evidence.
Everything else in this repository is proven by 61 structural guards that check the
*form*; these are the only checks that would speak to the *behaviour*, and they have
not been run yet. Printed here so "61 of 61 green" is never read as "the skill is
known to work".

## Runs

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

