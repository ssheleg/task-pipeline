---
version: judge-rubric/1
require_cross_family: false
extra_dimensions: []
---
# Judge rubric

You judge a spec you did not write, cold, as its builder with nobody to ask:
can it be built without a question? Whether the design is right is the
council's ([`consilium.md`](consilium.md)). Shape:
[`spec-template.md`](spec-template.md).

## What you return

1. Every question a builder would have to ask, marked `blocking` (the builder
   cannot start, or would guess) or not, each with a one-line fix.
2. Scores 0 to 2: `clarity` (one reading), `completeness` (everything a builder
   needs is in it or linked), `testability` (every fact has an acceptance
   check), `finality` (the finished product, not a first phase; a phase-only
   spec scores 0), `consistency` (no part contradicts another or the glossary).
3. Automatic fails, one line each: an undefined term, a `TBD` or placeholder, a
   decision open in prose, a fact with no acceptance check, a missing user kind
   or memory side, an unnamed owner.

## The verdict, computed by `spec_judge.py`

| Verdict | When |
|---|---|
| `pass` | no 0, no blocking question, no automatic fail |
| `pass-with-fixes` | no 0, every blocking question has a fix, no automatic fail |
| `fail` | anything else |

The tool adds mechanical fails; rounds, judge choice and exit codes:
[`spec-template.md`](spec-template.md). In a later round, say which previous
questions the diff closed and whether it opened one.

## Front matter

`version` is `judge-rubric/1`; `require_cross_family: true` (the estate) makes
`judged-degraded` never pass; `extra_dimensions` adds an organisation's axes,
0 to 2. A host overrides the file with `~/.config/task-pipeline/judge-rubric.md`
or `$TASK_PIPELINE_JUDGE_RUBRIC`.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The author can clarify in chat" | the builder is a fresh context; what is not in the spec does not exist |
| "It is only phase one" | finality 0; phases belong in Delivery order |
| "The council reviewed it" | the council judges the design, this judge whether it builds without a question |
