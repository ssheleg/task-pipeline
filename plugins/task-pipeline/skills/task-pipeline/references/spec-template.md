# Spec template: the final state, judged before it is built

A spec is a directory: `spec.md` in the sections below, in order, `spec.json`
beside it, and `judge/` written by `scripts/spec_judge.py`. An empty section
says "none". Judging: [`judge-rubric.md`](judge-rubric.md); the stage:
[`stage-03-spec.md`](stage-03-spec.md).

## spec.json (`spec/1`)

```json
{"schema": "spec/1", "id": "<project>-<slug>", "size": "S", "kind": "feature",
 "author_family": "<the model family that wrote the spec>", "status": "draft"}
```

A pull request cites it with the trailer `Spec: <id>@<commit>`; `spec_judge.py
find <id>` resolves the id under `docs/specs/*/` or `docs/plans/**/`.

## spec.md

```markdown
# Spec <id>: <the finished product in one line>

## Header

| Field | Value |
|---|---|
| id | <project>-<slug> |
| owner repositories | <every repository that changes, and what each owns> |
| size | S, M or L |
| kind | feature, fix, research, release or docs |
| memory side | <whose memory the work reads and writes> |
| supersedes | <specs, tools or rules this replaces, or none> |
| status | draft |

## Outcome
<what is true for whom when this is done; the owner's words quoted with date and place>

## Users
<every user kind the product has, what each sees or gets; a kind it does not reach says so>

## Final behaviour
1. <a fact in the present tense of the finished product>

## Data and contracts
<schemas, field names, file layouts, commands, exit codes>

## Boundaries
<what it does not do, and who does>

## Acceptance
- Fact 1: <the check that proves it, by command, test name or observation>
- Installed and observed: <the user kind that observes it, and how>

## Delivery order
<the phases, each leaving a working product; phases live here, never in Final behaviour>

## Waits and gates
<every wait with its owner and condition; every human gate named>

## Estimate
<measured work hours plus each named wait apart>

## Question ledger
<every question with its class and its decision; no decision left in prose>

## Glossary
<every term the canon glossary does not define>

## Judge record
<written by spec_judge.py; excluded from the content hash>
```

## Rules

Size: S is one repository and under a day of measured work, M up to three
repositories, L more or a contract change. Only `spec_judge.py` writes `judged`
or `judged-degraded`. The verdict is bound to SHA-256 of `spec.md` without
`## Judge record`; any edit makes it stale. Rounds: 1 reads the whole spec, 2
and 3 the diff and the open questions; round 3 only for one open blocking
question, then the spec stays `draft` and `judge/escalation.md` goes to the
owning project's coordinator. The judge is the strongest entry of
[`judge-models.json`](judge-models.json) of another family than
`author_family`; a same-family judge gives `judged-degraded`, valid for S and M
unless the rubric sets `require_cross_family: true`, never for L. `check
--verify` exits 0 judged, 1 not passing, 2 no or stale verdict, 3 cannot run.
Review by size: S the judge; M plus one validator of another family and the
council; L plus two blind validators of two families and the council
([`spec-protocol.md`](spec-protocol.md)).

## Rationalizations

| Excuse | Reality |
|---|---|
| "Delivery order is enough, the final state comes later" | the final state is the spec; delivery order is one section inside it |
| "It is too small for a template" | size S owes the same sections; most say "none" |
| "The judge record changes the file, so the hash changes" | the hash excludes that section by construction |
