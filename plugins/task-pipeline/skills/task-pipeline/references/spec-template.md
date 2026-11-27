# The spec template: the final state, judged before it is built

Every section at every size (empty: `none`); numbered facts, one Acceptance row each
([`spec-protocol.md`](spec-protocol.md) section 5). `size` S (one repository, a day), M (three), L
(more, or a contract); `kind` feature, fix, research, release, docs; `status` draft, judged,
judged-degraded, built, observed, superseded.

<!-- spec starts -->
# Spec: <the outcome in one line>

## Header

| Field | Value |
|---|---|
| id | `<id>` |
| owner repositories | <repository (what it owns)> |
| size | <size> |
| kind | <kind> |
| memory side | <personal or org:id> |
| supersedes | none |
| status | `draft` |

## Outcome

<Who asked, their words, date and source; what is true when it is done.>

## Users

<Every kind of user it touches and what each gets.>

## Final behaviour

1. <Name>: <what the finished product does, its inputs, outputs, states and owners.>

## Data and contracts

<Schemas, files, fields, exit codes; or none.>

## Boundaries

<What does not change, what is removed.>

## Acceptance

| Fact | Check |
|---|---|
| 1 | <a check that reads pass or fail> |
| installed and observed | <its user, on the real artefact> |

## Delivery order

1. <repository: what, by when>

## Waits and gates

<Owner, item and date of each wait; human gates; or none.>

## Estimate

<Kind, size, pieces, p50 and p85 hours.>

## Question ledger

<None open, or the ledger table.>

## Glossary

- <Term>: <definition>.

## Judge record

<spec_judge.py writes this.>
